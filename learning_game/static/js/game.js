let currentScore = 0;
let currentSubject = '';
let currentAnswer = null;
let playerName = '';

document.addEventListener('DOMContentLoaded', () => {
    playerName = localStorage.getItem('character') || 'Player';
    document.getElementById('playerName').textContent = `Welcome, ${playerName}!`;
});

async function startGame(subject) {
    currentSubject = subject;
    document.getElementById('subjectSelect').style.display = 'none';
    document.getElementById('gameArea').style.display = 'block';
    await nextQuestion();
}

async function nextQuestion() {
    document.getElementById('feedback').style.display = 'none';
    const questionDiv = document.getElementById('question');
    const answersDiv = document.getElementById('answers');
    
    try {
        let questionData;
        switch(currentSubject) {
            case 'math':
                questionDiv.innerHTML = '<p>Loading math problem...</p>';
                const response = await fetch('/api/math_problem?grade=1');
                questionData = await response.json();
                currentAnswer = questionData.answer;
                displayMathQuestion(questionData.problem);
                break;
            case 'reading':
                questionDiv.innerHTML = '<p>Loading word problem...</p>';
                const wordResponse = await fetch('/api/word_problem');
                questionData = await wordResponse.json();
                currentAnswer = questionData.word;
                displayWordQuestion(questionData);
                break;
            case 'science':
                questionDiv.innerHTML = '<p>Loading science fact...</p>';
                answersDiv.innerHTML = '';
                const scienceResponse = await fetch('/api/science_fact');
                if (!scienceResponse.ok) {
                    throw new Error('Failed to fetch science fact');
                }
                questionData = await scienceResponse.json();
                displayScienceFact(questionData);
                break;
        }
    } catch (error) {
        console.error('Error loading question:', error);
        questionDiv.innerHTML = `
            <p>Sorry, there was an error loading the content. Please try again!</p>
            <button onclick="nextQuestion()" class="next-btn">Try Again</button>
        `;
        answersDiv.innerHTML = '';
    }
}

function displayMathQuestion(problem) {
    document.getElementById('question').textContent = `What is ${problem}?`;
    const answersDiv = document.getElementById('answers');
    answersDiv.innerHTML = '';
    
    // Generate multiple choice options
    const correctAnswer = currentAnswer;
    const options = [correctAnswer];
    while (options.length < 4) {
        const wrongAnswer = correctAnswer + (Math.random() < 0.5 ? 1 : -1) * Math.floor(Math.random() * 5) + 1;
        if (!options.includes(wrongAnswer)) {
            options.push(wrongAnswer);
        }
    }
    
    // Shuffle options
    options.sort(() => Math.random() - 0.5);
    
    options.forEach(option => {
        const button = document.createElement('button');
        button.className = 'answer-btn';
        button.textContent = option;
        button.onclick = () => checkAnswer(option);
        answersDiv.appendChild(button);
    });
}

function displayWordQuestion(wordData) {
    document.getElementById('question').textContent = `What word means: "${wordData.definition}"?`;
    const answersDiv = document.getElementById('answers');
    answersDiv.innerHTML = '';
    // Use 'options' from backend and set currentAnswer to 'answer'
    const options = wordData.options;
    currentAnswer = wordData.answer;
    options.sort(() => Math.random() - 0.5);
    options.forEach(option => {
        const button = document.createElement('button');
        button.className = 'answer-btn';
        button.textContent = option;
        button.onclick = () => checkAnswer(option);
        answersDiv.appendChild(button);
    });
}

function displayScienceFact(factData) {
    const questionDiv = document.getElementById('question');
    const answersDiv = document.getElementById('answers');
    
    try {
        // Create the content with error handling for missing data
        const content = `
            <h3>${factData.fact || 'Interesting Science Fact'}</h3>
            ${factData.image ? `
                <img 
                    src="${factData.image}" 
                    alt="Science illustration" 
                    style="max-width: 300px; margin: 20px 0; display: none;"
                    onload="this.style.display='block'"
                    onerror="this.style.display='none'"
                >
            ` : ''}
            <p>${factData.explanation || 'Loading explanation...'}</p>
            ${factData.source ? `<p class="source">Source: ${factData.source}</p>` : ''}
        `;
        
        questionDiv.innerHTML = content;
        
        // Create and add the next button
        const button = document.createElement('button');
        button.className = 'next-btn';
        button.textContent = 'Next Fun Fact!';
        
        // Use async function for the click handler
        button.onclick = async () => {
            try {
                button.disabled = true;
                button.textContent = 'Loading...';
                await nextQuestion();
            } catch (error) {
                console.error('Error loading next question:', error);
                questionDiv.innerHTML = `
                    <p>Sorry, there was an error loading the next fact.</p>
                    <button onclick="nextQuestion()" class="next-btn">Try Again</button>
                `;
            } finally {
                button.disabled = false;
                button.textContent = 'Next Fun Fact!';
            }
        };
        
        answersDiv.innerHTML = '';
        answersDiv.appendChild(button);
    } catch (error) {
        console.error('Error displaying science fact:', error);
        questionDiv.innerHTML = `
            <p>Sorry, there was an error displaying this fact.</p>
            <button onclick="nextQuestion()" class="next-btn">Try Again</button>
        `;
        answersDiv.innerHTML = '';
    }
}

async function checkAnswer(userAnswer) {
    const feedback = document.getElementById('feedback');
    const feedbackText = document.getElementById('feedbackText');
    const feedbackGif = document.getElementById('feedbackGif');
    
    if (userAnswer === currentAnswer) {
        currentScore += 10;
        document.getElementById('score').textContent = currentScore;
        
        // Get a random celebration GIF
        const gifResponse = await fetch('/api/celebration_gif');
        const gifData = await gifResponse.json();
        
        feedbackText.textContent = getRandomPraise();
        feedbackGif.src = gifData.url;
    } else {
        feedbackText.textContent = getRandomEncouragement();
        feedbackGif.src = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcWM1ZWN0MmRqbWt0NmN1ZnBxdWR6Y2h6ZXBxbDdpY2wxaWR1NXV6dyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/26gsiXCNPx5MXg7Ac/giphy.gif";
    }
    
    feedback.style.display = 'block';
}

function getRandomPraise() {
    const praises = [
        `You rock, ${playerName}!`,
        `Amazing job, ${playerName}!`,
        `Wow! You're so smart, ${playerName}!`,
        `Fantastic work, ${playerName}!`,
        `You're doing great, ${playerName}!`,
        `Super duper, ${playerName}!`,
        `You're a star, ${playerName}!`,
        `Brilliant, ${playerName}!`
    ];
    return praises[Math.floor(Math.random() * praises.length)];
}

function getRandomEncouragement() {
    const encouragements = [
        "Almost there! Try again!",
        "You can do it! Give it another shot!",
        "Don't give up! You're learning!",
        "Keep trying! You're getting closer!",
        "That's not quite it, but you're doing great!"
    ];
    return encouragements[Math.floor(Math.random() * encouragements.length)];
}
