let answer = []; 
let attempts = 9; 
let gameOver = false; 

function initGame() {
    attempts = 9;
    gameOver = false;
    
    answer = generateRandomNumbers();
    console.log('정답:', answer); 
    
    document.getElementById('number1').value = '';
    document.getElementById('number2').value = '';
    document.getElementById('number3').value = '';
    
    document.getElementById('results').innerHTML = '';
    
    document.getElementById('game-result-img').src = '';
    
    document.getElementById('attempts').textContent = attempts;
    
    document.querySelector('.submit-button').disabled = false;
    
    document.getElementById('number1').focus();
}

function generateRandomNumbers() {
    const numbers = [];
    while (numbers.length < 3) {
        const randomNum = Math.floor(Math.random() * 10);
        if (!numbers.includes(randomNum)) {
            numbers.push(randomNum);
        }
    }
    return numbers;
}

function check_numbers() {
    if (gameOver) {
        return;
    }
    
    const input1 = document.getElementById('number1').value;
    const input2 = document.getElementById('number2').value;
    const input3 = document.getElementById('number3').value;
    
    if (input1 === '' || input2 === '' || input3 === '') {
        document.getElementById('number1').value = '';
        document.getElementById('number2').value = '';
        document.getElementById('number3').value = '';
        document.getElementById('number1').focus();
        return;
    }
    
    const userInput = [
        parseInt(input1),
        parseInt(input2),
        parseInt(input3)
    ];
    
    let strikes = 0;
    let balls = 0;
    
    for (let i = 0; i < 3; i++) {
        if (userInput[i] === answer[i]) {
            strikes++;
        } else if (answer.includes(userInput[i])) {
            balls++;
        }
    }
    
    attempts--;
    document.getElementById('attempts').textContent = attempts;
    
    displayResult(userInput, strikes, balls);
    
    if (strikes === 3) {
        endGame(true);
    } else if (attempts === 0) {
        endGame(false);
    }
    
    document.getElementById('number1').value = '';
    document.getElementById('number2').value = '';
    document.getElementById('number3').value = '';
    document.getElementById('number1').focus();
}

function displayResult(userInput, strikes, balls) {
    const resultsDiv = document.getElementById('results');
    
    const resultRow = document.createElement('div');
    resultRow.className = 'check-result';
    
    const leftDiv = document.createElement('div');
    leftDiv.className = 'left';
    leftDiv.textContent = userInput.join(' ');
    
    const centerDiv = document.createElement('div');
    centerDiv.textContent = ':';
    
    const rightDiv = document.createElement('div');
    rightDiv.className = 'right';
    
    if (strikes === 0 && balls === 0) {
        const outSpan = document.createElement('span');
        outSpan.className = 'num-result out';
        outSpan.textContent = 'O';
        rightDiv.appendChild(outSpan);
    } else {
        const strikeNumSpan = document.createElement('span');
        strikeNumSpan.className = 'num-result';
        strikeNumSpan.textContent = strikes + ' ';
        rightDiv.appendChild(strikeNumSpan);
        
        const strikeLabel = document.createElement('span');
        strikeLabel.className = 'num-result strike';
        strikeLabel.textContent = 'S';
        rightDiv.appendChild(strikeLabel);
        
        rightDiv.appendChild(document.createTextNode(' '));
        
        const ballNumSpan = document.createElement('span');
        ballNumSpan.className = 'num-result';
        ballNumSpan.textContent = balls + ' ';
        rightDiv.appendChild(ballNumSpan);
        
        const ballLabel = document.createElement('span');
        ballLabel.className = 'num-result ball';
        ballLabel.textContent = 'B';
        rightDiv.appendChild(ballLabel);
    }
    
    resultRow.appendChild(leftDiv);
    resultRow.appendChild(centerDiv);
    resultRow.appendChild(rightDiv);
    
    resultsDiv.appendChild(resultRow);
}

function endGame(isWin) {
    gameOver = true;
    
    const resultImg = document.getElementById('game-result-img');
    if (isWin) {
        resultImg.src = './success.png';
        resultImg.alt = 'Success!!';
    } else {
        resultImg.src = './fail.png';
        resultImg.alt = 'Fail..';
    }
    
    document.querySelector('.submit-button').disabled = true;
}

document.addEventListener('DOMContentLoaded', function() {
    const number1 = document.getElementById('number1');
    const number2 = document.getElementById('number2');
    const number3 = document.getElementById('number3');
    
    number1.addEventListener('keyup', function(event) {
        if (this.value.length === 1) {
            number2.focus();
        }
    });
    
    number2.addEventListener('keyup', function(event) {
        if (this.value.length === 1) {
            number3.focus();
        }
    });
    
    number3.addEventListener('keyup', function(event) {
        if (event.key === 'Enter' && this.value.length === 1) {
            check_numbers();
        }
    });
    
    initGame();
});