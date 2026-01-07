/**
 * Lógica del juego Akinator - Frontend
 */

// Estado global del juego
let gameState = {
    sessionId: null,
    currentQuestion: null,
    questionCount: 0,
    guessedCharacter: null
};

const API_BASE = '';

// ===== INICIALIZACIÓN =====
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    setupConfetti();
});

// ===== FUNCIONES DE JUEGO =====

async function startGame() {
    try {
        const response = await fetch(`${API_BASE}/api/game/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        gameState.sessionId = data.session_id;
        gameState.currentQuestion = data.question;
        gameState.questionCount = 1;
        
        // Cambiar a pantalla de juego
        document.getElementById('heroSection').classList.add('hidden');
        document.getElementById('gameSection').classList.remove('hidden');
        
        // Mostrar primera pregunta
        displayQuestion(data);
        
    } catch (error) {
        console.error('Error starting game:', error);
        alert('Error al iniciar el juego');
    }
}

async function answerQuestion(answer) {
    try {
        const response = await fetch(`${API_BASE}/api/game/answer`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: gameState.sessionId,
                question_id: gameState.currentQuestion.id,
                answer: answer
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        // Verificar tipo de respuesta
        if (data.type === 'guess') {
            // Mostrar adivinanza
            showGuessModal(data.character);
            gameState.guessedCharacter = data.character;
        } else if (data.type === 'give_up') {
            // No pudo adivinar
            showAddCharacterModal();
        } else {
            // Siguiente pregunta
            gameState.currentQuestion = data.question;
            gameState.questionCount = data.question_count;
            displayQuestion(data);
        }
        
    } catch (error) {
        console.error('Error answering question:', error);
        alert('Error al procesar respuesta');
    }
}

function displayQuestion(data) {
    // Actualizar texto de pregunta
    document.getElementById('questionText').textContent = data.question.text;
    
    // Actualizar progreso
    const progress = data.progress || 0;
    document.getElementById('progressFill').style.width = progress + '%';
    document.getElementById('progressText').textContent = `Pregunta ${gameState.questionCount}`;
    
    // Actualizar candidatos
    if (data.candidates_remaining !== undefined) {
        document.getElementById('candidatesCount').textContent = data.candidates_remaining;
    }
    
    // Animar entrada de pregunta
    const questionContainer = document.querySelector('.question-container');
    questionContainer.style.animation = 'none';
    setTimeout(() => {
        questionContainer.style.animation = 'slideIn 0.5s ease-out';
    }, 10);
}

// ===== MODALES =====

function showGuessModal(character) {
    document.getElementById('guessedCharacter').textContent = character.name;
    document.getElementById('guessedDescription').textContent = character.description || 'Personaje misterioso';
    document.getElementById('guessModal').classList.remove('hidden');
}

async function confirmGuess(correct) {
    try {
        const response = await fetch(`${API_BASE}/api/game/confirm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: gameState.sessionId,
                character_id: gameState.guessedCharacter.id,
                correct: correct
            })
        });
        
        const data = await response.json();
        
        // Cerrar modal de adivinanza
        document.getElementById('guessModal').classList.add('hidden');
        
        if (correct) {
            // Mostrar resultado exitoso
            showResultModal(true, data.questions_used);
            // Lanzar confetti
            launchConfetti();
        } else {
            // Mostrar formulario para agregar personaje
            showAddCharacterModal();
        }
        
    } catch (error) {
        console.error('Error confirming guess:', error);
        alert('Error al confirmar adivinanza');
    }
}

function showResultModal(success, questionsUsed) {
    const modal = document.getElementById('resultModal');
    const icon = document.getElementById('resultIcon');
    const title = document.getElementById('resultTitle');
    const message = document.getElementById('resultMessage');
    
    if (success) {
        icon.textContent = '🎉';
        title.textContent = '¡Éxito!';
        message.textContent = 'Adiviné tu personaje correctamente';
    } else {
        icon.textContent = '😅';
        title.textContent = '¡Ups!';
        message.textContent = 'No pude adivinar esta vez, pero aprenderé';
    }
    
    document.getElementById('questionsUsed').textContent = questionsUsed || gameState.questionCount;
    modal.classList.remove('hidden');
}

async function showAddCharacterModal() {
    const modal = document.getElementById('addCharacterModal');
    
    // Cargar preguntas básicas
    try {
        const response = await fetch(`${API_BASE}/api/questions`);
        const data = await response.json();
        
        // Mostrar las primeras 10 preguntas más importantes
        const questions = data.questions.slice(0, 10);
        const questionsContainer = document.getElementById('characterQuestions');
        questionsContainer.innerHTML = '';
        
        questions.forEach(question => {
            const div = document.createElement('div');
            div.className = 'question-item';
            div.innerHTML = `
                <label>${question.text}</label>
                <select data-attribute="${question.attribute_key}">
                    <option value="2">Sí</option>
                    <option value="1">Probablemente sí</option>
                    <option value="0" selected>No sé</option>
                    <option value="-1">Probablemente no</option>
                    <option value="-2">No</option>
                </select>
            `;
            questionsContainer.appendChild(div);
        });
        
        modal.classList.remove('hidden');
        
    } catch (error) {
        console.error('Error loading questions:', error);
    }
}

function closeAddCharacterModal() {
    document.getElementById('addCharacterModal').classList.add('hidden');
    showResultModal(false, gameState.questionCount);
}

// ===== FORMULARIO DE PERSONAJE =====

document.getElementById('addCharacterForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('characterName').value;
    const description = document.getElementById('characterDescription').value;
    
    // Recopilar atributos
    const attributes = {};
    const selects = document.querySelectorAll('#characterQuestions select');
    selects.forEach(select => {
        const key = select.getAttribute('data-attribute');
        const value = parseInt(select.value);
        attributes[key] = value;
    });
    
    try {
        const response = await fetch(`${API_BASE}/api/character/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                description: description,
                attributes: attributes
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Cerrar modal de agregar personaje
            document.getElementById('addCharacterModal').classList.add('hidden');
            
            // Mostrar resultado
            showResultModal(false, gameState.questionCount);
            
            // Mensaje de éxito
            setTimeout(() => {
                alert(`¡Gracias! He aprendido sobre ${name}`);
            }, 500);
        } else {
            alert('Error: ' + data.error);
        }
        
    } catch (error) {
        console.error('Error adding character:', error);
        alert('Error al agregar personaje');
    }
});

// ===== RESET =====

function resetGame() {
    // Limpiar estado
    gameState = {
        sessionId: null,
        currentQuestion: null,
        questionCount: 0,
        guessedCharacter: null
    };
    
    // Cerrar modales
    document.getElementById('resultModal').classList.add('hidden');
    document.getElementById('guessModal').classList.add('hidden');
    document.getElementById('addCharacterModal').classList.add('hidden');
    
    // Volver a hero
    document.getElementById('gameSection').classList.add('hidden');
    document.getElementById('heroSection').classList.remove('hidden');
    
    // Recargar estadísticas
    loadStats();
}

// ===== ESTADÍSTICAS =====

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        const data = await response.json();
        
        const statsPreview = document.getElementById('statsPreview');
        const statItems = statsPreview.querySelectorAll('.stat-item');
        
        if (statItems.length >= 3) {
            statItems[0].querySelector('.stat-value').textContent = data.database?.total_characters || 0;
            statItems[1].querySelector('.stat-value').textContent = data.total_games || 0;
            statItems[2].querySelector('.stat-value').textContent = (data.success_rate || 0) + '%';
        }
        
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// ===== CONFETTI =====

let confettiCanvas;
let confettiCtx;
let confettiParticles = [];

function setupConfetti() {
    confettiCanvas = document.getElementById('confetti');
    confettiCtx = confettiCanvas.getContext('2d');
    confettiCanvas.width = window.innerWidth;
    confettiCanvas.height = window.innerHeight;
    
    window.addEventListener('resize', () => {
        confettiCanvas.width = window.innerWidth;
        confettiCanvas.height = window.innerHeight;
    });
}

function launchConfetti() {
    const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'];
    
    for (let i = 0; i < 100; i++) {
        confettiParticles.push({
            x: Math.random() * confettiCanvas.width,
            y: -10,
            size: Math.random() * 8 + 4,
            speedY: Math.random() * 3 + 2,
            speedX: Math.random() * 2 - 1,
            color: colors[Math.floor(Math.random() * colors.length)],
            rotation: Math.random() * 360,
            rotationSpeed: Math.random() * 10 - 5
        });
    }
    
    animateConfetti();
}

function animateConfetti() {
    confettiCtx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);
    
    confettiParticles.forEach((particle, index) => {
        particle.y += particle.speedY;
        particle.x += particle.speedX;
        particle.rotation += particle.rotationSpeed;
        
        confettiCtx.save();
        confettiCtx.translate(particle.x, particle.y);
        confettiCtx.rotate(particle.rotation * Math.PI / 180);
        confettiCtx.fillStyle = particle.color;
        confettiCtx.fillRect(-particle.size / 2, -particle.size / 2, particle.size, particle.size);
        confettiCtx.restore();
        
        // Remover partículas que salieron de la pantalla
        if (particle.y > confettiCanvas.height) {
            confettiParticles.splice(index, 1);
        }
    });
    
    if (confettiParticles.length > 0) {
        requestAnimationFrame(animateConfetti);
    }
}
