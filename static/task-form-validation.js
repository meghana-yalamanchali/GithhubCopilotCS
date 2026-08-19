(function () {
    const form = document.getElementById('add-task-form');

    if (!form) {
        return;
    }

    const taskInput = document.getElementById('new-item');
    const dueDateInput = document.getElementById('due-date');
    const fields = [
        { input: taskInput, error: document.getElementById('new-item-error'), name: 'newItem' },
        { input: dueDateInput, error: document.getElementById('due-date-error'), name: 'duedate' }
    ];

    form.noValidate = true;

    function validateDueDate(input) {
        if (!input.value) {
            return 'Enter a due date.';
        }

        if (!input.validity.valid) {
            return 'Enter a valid calendar date.';
        }

        const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(input.value);
        if (!match) {
            return 'Enter a valid calendar date.';
        }

        const year = Number(match[1]);
        const month = Number(match[2]);
        const day = Number(match[3]);
        const selectedDate = new Date(year, month - 1, day);
        if (
            selectedDate.getFullYear() !== year ||
            selectedDate.getMonth() !== month - 1 ||
            selectedDate.getDate() !== day
        ) {
            return 'Enter a valid calendar date.';
        }

        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        if (selectedDate <= today) {
            return 'Choose a due date later than today.';
        }

        return '';
    }

    function renderField(field, message) {
        const isInvalid = Boolean(message);
        field.error.textContent = message;
        field.input.classList.toggle('input-invalid', isInvalid);

        if (isInvalid) {
            field.input.setAttribute('aria-invalid', 'true');
            field.input.setAttribute('aria-describedby', field.error.id);
            return;
        }

        field.input.removeAttribute('aria-invalid');
        field.input.removeAttribute('aria-describedby');
    }

    form.addEventListener('submit', function (event) {
        const errors = {
            newItem: taskInput.value.trim() ? '' : 'Enter a task name.',
            duedate: validateDueDate(dueDateInput)
        };
        let firstInvalidField = null;

        fields.forEach(function (field) {
            const message = errors[field.name];
            renderField(field, message);

            if (message && !firstInvalidField) {
                firstInvalidField = field.input;
            }
        });

        if (firstInvalidField) {
            event.preventDefault();
            firstInvalidField.focus();
        }
    });
}());