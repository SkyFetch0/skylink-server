function addProject(projectName, Type, projectType) {
    alert(projectName + " | " + Type + " | " + projectType + kfZpM9C3);
    if (projectName && Type && projectType) {
        if (!kfZpM9C3 && !cZ3pi4AzfC) {
            alert("Auth Key Not Found");
        } else {
            var jsonData = {
                user_auth: kfZpM9C3,
                user_id: cZ3pi4AzfC,
                projectName: projectName,
                type: Type
            };

            fetch('/create_container', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(jsonData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    console.log('Container created successfully, CID:', data.cid);
                    alert('Container created successfully, CID: ' + data.cid);
                } else {
                    console.error('Failed to create container. Response:', data);
                    alert('Failed to create container: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred: ' + error.message);
            });
        }
    }
}

function confirmProject() {
    var projectName = document.getElementById('modalProjectName').value; 
    var type = document.getElementById('modalType').value; 
    var projectType = document.getElementById('projectType').value; 

    if (projectName && type && projectType) {
      console.log(projectName);
      if(type === "iot") {
         addProject(projectName,type,projectType);

      } 
        $('.close').click(); 

    } else {
        alert("Please enter name.");
    }
}
function devicemodal(type) {
    var typearea = document.getElementById('modalType');
    var modalname = document.getElementById('panelModalLabel');
    if(type === "iot") {
        modalname.textContent = "Create IoT Project";

    }
    typearea.value = type;
}