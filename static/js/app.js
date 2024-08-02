let optionCount = {
    "question1": 1
};
let increment = 1;
let dictionary = {
    "questions": []
}


function addOption(quest, n) {
    optionCount['question'+quest] ++

    // optionCount = optionCount[]
    let optionCount2 = optionCount['question'+quest]

    const optionsContainer = document.getElementById('optionsContainer-' + n);
    const newOption = document.createElement('input');
    const newCheckBox = document.createElement('input');
    newOption.type = 'text';
    newOption.placeholder = `Option ${optionCount2}`;
    newOption.classList.add('option');
    newOption.name = 'answer-' + n + "-" + optionCount2
    newOption.required = true
    newCheckBox.type = 'radio';
    newCheckBox.name = `option` + n;
    newCheckBox.id = `option${optionCount2}`;
    newCheckBox.value = optionCount2
    newCheckBox.classList.add('option-checkbox');
    optionsContainer.appendChild(newCheckBox);
    optionsContainer.appendChild(newOption);
}

function addQuestion() {
    increment++;
    optionCount[`question${increment}`] = 1;


    const questions = document.getElementById('questions');

    const questionContainer = document.createElement('div');
    questionContainer.className = 'questionContainer';

    const textarea = document.createElement('textarea');
    textarea.name = `question${increment}`;
    textarea.id = 'questionText';
    textarea.placeholder = 'Question text';
    textarea.required = true;

    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.name = `file${increment}`;
    fileInput.className = 'file';

    const optionsContainer = document.createElement('div');
    optionsContainer.id = `optionsContainer-${increment}`;
    optionsContainer.className = 'optionsContainer';

    const radioInput = document.createElement('input');
    radioInput.type = 'radio';
    radioInput.name = `option${increment}`;
    radioInput.value = '1';
    radioInput.className = 'option-checkbox';
    radioInput.checked = true;

    const textInput = document.createElement('input');
    textInput.type = 'text';
    textInput.name = `answer-${increment}-1`;
    textInput.placeholder = 'Option 1';
    textInput.className = 'option';
    textInput.required = true

    optionsContainer.appendChild(radioInput);
    optionsContainer.appendChild(textInput);

    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'buttonContainer';

    const addButton = document.createElement('button');
    addButton.type = 'button';
    addButton.textContent = 'Add Option';
    addButton.onclick = () => addOption(increment, increment);

    buttonContainer.appendChild(addButton);

    questionContainer.appendChild(textarea);
    questionContainer.appendChild(fileInput);
    questionContainer.appendChild(optionsContainer);
    questionContainer.appendChild(buttonContainer);

    questions.appendChild(questionContainer);
}
