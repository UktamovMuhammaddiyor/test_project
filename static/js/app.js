let increment = 1,
    increment_for_grade = 1;
let dictionary = {
    "questions": []
}
let eventListener = 0

function addOption(quest, n) {

    let a = document.getElementById(`optionsContainer-${n}`)
    let optionCount2 = Number(a.children[a.children.length - 1].placeholder.slice(-1)) + 1

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
    
    let count = document.getElementsByClassName("optionsContainer")
    count = count[count.length - 1].id
    let chiziq = count.indexOf('-')
    count = count.slice(chiziq + 1)
    
    increment = Number(count) + 1

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
    buttonContainer.innerHTML += `<div class="buttonContainer"><button type="button" onclick="addOption(${increment}, ${increment})">Add Option</button></div>`;

    questionContainer.appendChild(textarea);
    questionContainer.appendChild(fileInput);
    questionContainer.appendChild(optionsContainer);
    questionContainer.appendChild(buttonContainer);

    questions.appendChild(questionContainer);
}

function addGrade() {
    increment_for_grade += 1
    const forms = document.getElementById('score-form');
    const to = document.getElementById(`to${increment_for_grade-1}`);
    const count = document.getElementById('number_of_questions');
    const container = document.createElement('div');
    
    container.className = 'scores';
    let options_from = ""
    let options_to = ""
    for (let index = 0; index < Number(count.value); index++) {
        let element
        if (Number(to.value) === (index - 1)) {
            element = `<option value="${index}" selected>${index}</option>`;  
        } else {
            element = `<option value="${index}">${index}</option>`;
        }
        options_from += element
        options_to += element
    }
    options_from += `<option value="${count.value}">${count.value}</option>`
    options_to += `<option value="${count.value}" selected>${count.value}</option>`
    
    container.innerHTML = `<div class="select-score"><label for="from${increment_for_grade}">From</label><select name="from${increment_for_grade}" id="from${increment_for_grade}">${options_from}</select></div><div class="select-score"><label for="to${increment_for_grade}">To</label><select name="to${increment_for_grade}" id="to${increment_for_grade}">${options_to}</select></div><input type="text" name="score${increment_for_grade}" class="score" placeholder="daraja..." required>`

    forms.appendChild(container)
}

function deleteSubject(id, name) {
    const element = document.getElementById("deleteSubjectContainer")
    element.innerHTML = `<div class="container">
            <p>Do you really want delete '${name}' subject?</p>
        <div class="buttonContainer">
            <a href="deleteSubject?id=${Number(id)}" id="deleteSubject">Yes</a>
            <a onclick="cancelDeleteSubject()">No</a>
        </div>
        </div>`
    element.style.display = "flex"
    document.addEventListener("keypress", eventListenerFunction)
    element.addEventListener("click", clickWindowOnDeleteSubject)
}
function eventListenerFunction (key) {
    if(key['key'] === "Enter") {
        document.getElementById('deleteSubject').click()
    }
}
function cancelDeleteSubject() {
    document.getElementById("deleteSubjectContainer").style.display = "none"
    document.removeEventListener("keypress", eventListenerFunction)
    document.getElementById("deleteSubjectContainer").removeEventListener("click", clickWindowOnDeleteSubject)
}

function clickWindowOnDeleteSubject() {
    cancelDeleteSubject()
}