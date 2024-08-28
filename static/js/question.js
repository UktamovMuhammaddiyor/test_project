document.addEventListener("DOMContentLoaded", function() {
    // Select all radio buttons
    const form = document.getElementById('questionForm');
    form.reset();
    
    const radioButtons = document.querySelectorAll('input[type="radio"]');
    let subject_id = document.getElementById("subject_id")
    let test = {
        "subject_id": subject_id.value,
        "answers": [],
    } 

    // Add event listener to each radio button
    radioButtons.forEach(radio => {
        radio.addEventListener('change', function() {
            let subject_count = document.getElementById("subject_count")
            subject_count = Number(subject_count.value)
            console.log(`Radio button with ID ${this.id} was clicked. Value: ${this.value}`);
            // Add your custom event handling code here
            let chiziq = this.id.indexOf('-')
            let name = this.id.slice(0, chiziq),
                question = document.getElementById(name), 
                question_id = Number(name.slice(6, this.id.length)),
                previous_question = document.getElementById(`question${question_id}`),
                next_question = document.getElementById(`question${question_id+1}`)
            // console.log(name)
            test['answers'].push({
                    "id": question.value,
                    "answer": this.value,
                })

            if (question_id === subject_count) {
                addJsonToForm(test)
                document.getElementById('questionForm').submit();
            } else {
                previous_question.classList.remove("active")
                previous_question.classList.add("noactive")
                next_question.classList.add("active")
                document.getElementById("count").innerHTML = question_id + 1
            }
            

        });
    });
});

function addJsonToForm(jsonData) {
    const form = document.getElementById('questionForm');
    const hiddenInput = document.createElement('input');
    hiddenInput.type = 'hidden';
    hiddenInput.name = 'answers';
    hiddenInput.value = JSON.stringify(jsonData);
    form.appendChild(hiddenInput);
}


