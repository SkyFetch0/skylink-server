function saveButtons(userKey,contKey) {
    var buttons = document.getElementsByClassName('dragme');
    var buttonPositions = [];

    for (var i = 0; i < buttons.length; i++) {
        var button = buttons[i];
        buttonPositions.push({
            auth: userKey,
            container: contKey,
            user_id: cZ3pi4AzfC,
            button_id: button.id,
            button_name: button.getAttribute('data-name'),
            left: button.style.left || '0px',  
            top: button.style.top || '0px',    
            class: button.className,
            'data-item': button.getAttribute('data-item'),
            'data-contype': button.getAttribute('data-contype'),
            'data-status': button.getAttribute('data-status') || 'OFF' 
        });
    }

    localStorage.setItem('buttonPositions', JSON.stringify(buttonPositions));

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/save_buttons', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            console.log('Button positions saved successfully');
        } else {
            console.error('Failed to save button positions. Status:', xhr.status, 'Response:', xhr.responseText);
        }
    };
    xhr.send(JSON.stringify(buttonPositions));
}
function loadButtons() {
    var buttonPositions = JSON.parse(localStorage.getItem('buttonPositions'));

    if (buttonPositions) {
        for (var i = 0; i < buttonPositions.length; i++) {
            var buttonData = buttonPositions[i];

            if (buttonData['data-contype'] === 'button') {
                addButton(buttonData.button_name);
                var newButton = document.getElementById(buttonData.button_id);
                newButton.style.left = buttonData.left;
                newButton.style.top = buttonData.top;
                newButton.setAttribute('data-status', buttonData['data-status']);
                newButton.className = buttonData.class;
                newButton.innerText = buttonData['data-status'] === 'ON' ? 'On' : 'Off';
            } else if (buttonData['data-contype'] === 'switch') {
                addSwitch(buttonData.button_name);
                var newSwitch = document.getElementById(buttonData.button_id);
                newSwitch.style.left = buttonData.left;
                newSwitch.style.top = buttonData.top;
                var switchInput = newSwitch.querySelector('input[type="checkbox"]');
                switchInput.checked = buttonData['data-status'] === 'ON';
                newSwitch.className = buttonData.class;
            } else if (buttonData['data-contype'] === 'message') {
                addMessageInput(buttonData.button_name);
                var newMessageInput = document.getElementById(buttonData.button_id);
                newMessageInput.style.left = buttonData.left;
                newMessageInput.style.top = buttonData.top;
                newMessageInput.className = buttonData.class;
            }
        }
    }
}


function listenToAllSwitches() {
    var labels = document.querySelectorAll('label[data-contype="switch"]');

    labels.forEach(function(label) {
        var switchInput = label.querySelector('input[type="checkbox"]');
        
        if (switchInput) {
            switchInput.addEventListener('change', function() {
                var isChecked = switchInput.checked;
                var buttonName = switchInput.getAttribute('name');
                var newStatus = isChecked ? 'ON' : 'OFF';

                var formData = new FormData();
                formData.append('auth_code', "afc342");
                formData.append('device', buttonName);
                formData.append('is_checked', newStatus);

                var xhr = new XMLHttpRequest();
                xhr.open('POST', '/toggle_device', true);
                xhr.setRequestHeader('Content-Type', 'application/json');
                xhr.onload = function() {
                    if (xhr.status === 200) {
                        console.log('Device status toggled successfully');
                    } else {
                        console.error('Failed to toggle device status. Status:', xhr.status, 'Response:', xhr.responseText);
                    }
                };

                var jsonData = {};
                for (var [key, value] of formData.entries()) {
                    jsonData[key] = value;
                }

                xhr.send(JSON.stringify(jsonData));
            });
        }
    });
}

listenToAllSwitches();

function addSwitch(buttonName) {

    var authCode = generateAuthCode();
    var switchId = 'button_' + authCode; 

    var buttonContainer = document.getElementById('buttonContainer');
    var switchLabel = document.createElement('label');
    switchLabel.setAttribute('id', switchId);
    switchLabel.setAttribute('data-contype', "switch");
    switchLabel.setAttribute('data-name', buttonName);

    switchLabel.setAttribute('class', 'switch dragme ' + switchId); 
    switchLabel.setAttribute('data-item', buttonContainer.children.length); 
    switchLabel.setAttribute('draggable', true); 

    var switchInput = document.createElement('input');
    switchInput.setAttribute('type', 'checkbox');
    switchInput.setAttribute('id', 'myCheckbox');
    switchInput.setAttribute('name', buttonName); 

    var switchSpan = document.createElement('span');
    switchSpan.setAttribute('class', 'slider round');

    switchLabel.appendChild(switchInput);
    switchLabel.appendChild(switchSpan);

    buttonContainer.appendChild(switchLabel);

    
    switchInput.addEventListener('change', function() {
        var isChecked = switchInput.checked;
        var buttonName = switchInput.getAttribute('name'); 
        var newStatus = isChecked ? 'ON' : 'OFF';

        var formData = new FormData();
        formData.append('auth_code', "afc342"); 
        formData.append('device', buttonName); 
        formData.append('type', "switch"); 

        formData.append('action', newStatus);

        console.log(isChecked + " N " + buttonName + " Z " + newStatus)
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/toggle_device', true);
xhr.setRequestHeader('Content-Type', 'application/json'); 
xhr.onload = function() {
    if (xhr.status === 200) {
        console.log('Device status toggled successfully');
    } else {
        console.error('Failed to toggle device status. Status:', xhr.status, 'Response:', xhr.responseText);
    }
};

        var jsonData = {};
        for (var [key, value] of formData.entries()) {
            jsonData[key] = value;
        }

        xhr.send(JSON.stringify(jsonData));

    });
    switchLabel.addEventListener('dragstart', function(event) {
        event.dataTransfer.setData('text/plain', event.target.id);
        event.dataTransfer.setData('text/prevIndex', event.target.getAttribute('data-item'));
    });

    switchLabel.addEventListener('dragstart', drag_start, false);
    switchLabel.addEventListener('dragover', drag_over, false);
    switchLabel.addEventListener('drop', drop, false);
}
           
             
function addMessageInput(buttonName) {
    var authCode = generateAuthCode();
    var inputId = 'input_' + authCode; 

    var buttonContainer = document.getElementById('buttonContainer');
    var formInline = document.createElement('div');
    formInline.setAttribute('class', 'form-inline dragme ' + inputId);
    formInline.setAttribute('id', inputId);
    formInline.setAttribute('data-contype', "message");
    formInline.setAttribute('data-name', buttonName);
    formInline.setAttribute('data-item', buttonContainer.children.length);
    formInline.setAttribute('draggable', true);

    var label = document.createElement('label');
    label.setAttribute('class', 'sr-only');
    label.setAttribute('for', inputId);
    label.innerText = 'Message | ' + buttonName;

    var input = document.createElement('input');
    input.setAttribute('type', 'text');
    input.setAttribute('class', 'form-control mb-2 mr-sm-2');
    input.setAttribute('id', inputId);
    input.setAttribute('placeholder', 'Message');

    var button = document.createElement('button');
    button.setAttribute('type', 'submit');
    button.setAttribute('class', 'btn btn-primary mb-2');
    button.innerText = 'Send';

    formInline.appendChild(label);
    formInline.appendChild(input);
    formInline.appendChild(button);

    buttonContainer.appendChild(formInline);

    button.addEventListener('click', function() {
        var inputValue = input.value;
        var formData = new FormData();

        formData.append('auth_code', "afc342"); 
        formData.append('device', buttonName); 
        formData.append('type', "message"); 
        formData.append('action', inputValue); 

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/toggle_device', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onload = function() {
            if (xhr.status === 200) {
                console.log('Message sent successfully');
            } else {
                console.error('Failed to send message. Status:', xhr.status, 'Response:', xhr.responseText);
            }
        };

        var jsonData = {};
        for (var [key, value] of formData.entries()) {
            jsonData[key] = value;
        }

        xhr.send(JSON.stringify(jsonData));
    });

    formInline.addEventListener('dragstart', function(event) {
        event.dataTransfer.setData('text/plain', event.target.id);
        event.dataTransfer.setData('text/prevIndex', event.target.getAttribute('data-item'));
    });

    formInline.addEventListener('dragstart', drag_start, false);
    formInline.addEventListener('dragover', drag_over, false);
    formInline.addEventListener('drop', drop, false);
}


function addButton(buttonName) {
    var authCode = generateAuthCode();
    var buttonId = 'button_' + authCode; 
    var buttonContainer = document.getElementById('buttonContainer');
    var newButton = document.createElement('button');
    
    newButton.setAttribute('id', buttonId);
    newButton.setAttribute('data-contype', "button");
    newButton.setAttribute('data-name', buttonName);
    newButton.setAttribute('data-status', "OFF"); 
    newButton.setAttribute('class', 'toggleButton dragme ' + buttonId); 
    newButton.setAttribute('data-item', buttonContainer.children.length); 
    newButton.setAttribute('draggable', true); 
    newButton.innerText = buttonName || 'New Button';
    
    newButton.addEventListener('click', function() {
        var buttonName = newButton.getAttribute('data-name');
        var buttonStatus = newButton.getAttribute('data-status');
        var formData = new FormData();
        formData.append('auth_code', "afc342"); 
        formData.append('device', buttonName); 
        formData.append('type', "button"); 
        
        if (buttonStatus === "OFF") {
            formData.append('action', 'ON');
            newButton.setAttribute('data-status', "ON"); 
            newButton.innerText = "On"; 
            newButton.classList.remove("toggleButtonoff"); 
        } else {
            formData.append('action', 'OFF');
            newButton.setAttribute('data-status', "OFF"); 
            newButton.innerText = "Off"; 
            newButton.classList.add("toggleButtonoff"); 

        }

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/toggle_device', true);
        xhr.setRequestHeader('Content-Type', 'application/json'); 
        xhr.onload = function() {
            if (xhr.status === 200) {
                console.log('Button clicked successfully');
            } else {
                console.error('Failed to handle button click. Status:', xhr.status, 'Response:', xhr.responseText);
            }
        };
        
        var jsonData = {};
        for (var [key, value] of formData.entries()) {
            jsonData[key] = value;
        }
        
        xhr.send(JSON.stringify(jsonData));
    });
    
    newButton.addEventListener('dragstart', function(event) {
        event.dataTransfer.setData('text/plain', event.target.id);
        event.dataTransfer.setData('text/prevIndex', event.target.getAttribute('data-item')); 
    });
    
    newButton.addEventListener('dragstart', drag_start, false);
    newButton.addEventListener('dragover', drag_over, false);
    newButton.addEventListener('drop', drop, false);
    
    buttonContainer.appendChild(newButton);
}

       

        function generateAuthCode() {
            return Math.random().toString(36).substr(2, 9);
        }

        document.addEventListener('DOMContentLoaded', (event) => {
            var dm = document.getElementsByClassName('dragme');
        
            for (var i = 0; i < dm.length; i++) {
                dm[i].addEventListener('dragstart', drag_start, false);
                document.body.addEventListener('dragover', drag_over, false);
                document.body.addEventListener('drop', drop, false);
            }
        });
        
        function drag_start(event) {
            var style = window.getComputedStyle(event.target, null);
            event.dataTransfer.setData("text/plain", (parseInt(style.getPropertyValue("left"), 10) - event.clientX) + ',' + (parseInt(style.getPropertyValue("top"), 10) - event.clientY) + ',' + event.target.id);
        }
        
        function drag_over(event) {
            event.preventDefault();
            return false;
        }
        
        function drop(event) {
            var offset = event.dataTransfer.getData("text/plain").split(',');
            var dm = document.getElementById(offset[2]);
        
            if (dm) {
                dm.style.left = (event.clientX + parseInt(offset[0], 10)) + 'px';
                dm.style.top = (event.clientY + parseInt(offset[1], 10)) + 'px';
            } else {
                console.error('Hedef öğe bulunamadı veya geçersiz.');
            }
            event.preventDefault();
            return false;
        }
        
        function addDragEvents(element) {
            element.addEventListener('dragstart', drag_start, false);
            document.body.addEventListener('dragover', drag_over, false);
            document.body.addEventListener('drop', drop, false);
        }
        

        function confirmAddSwitch() {
            var buttonName = document.getElementById('modalSwitchName').value; 
            var type = document.getElementById('modalType').value; 

            if (buttonName) {
              console.log(buttonName);
              if(type === "switch") {
                 addSwitch(buttonName);

              } else if(type === "button") {
                addButton(buttonName);
              } else if(type === "textarea") {
                addMessageInput(buttonName);
              }
                $('.close').click(); 
    
            } else {
                alert("Please enter name.");
            }
        }
    function openmodal(type) {
        var typearea = document.getElementById('modalType');

        typearea.value = type;
    }