function go() {
    localStorage.setItem("text", "Converting submissions...")
    document.getElementById('text').innerHTML = "Converting submissions..."
    chrome.tabs.query({currentWindow: true, active: true}, function (tabs){
        var activeTab = tabs[0];
        chrome.tabs.sendMessage(activeTab.id, {"message": "start"});
    });
}

function create() {
    localStorage.setItem("text", "Creating assignment...")
    document.getElementById('text').innerHTML = "Creating assignment..."
    chrome.tabs.query({currentWindow: true, active: true}, function (tabs){
        var activeTab = tabs[0];
        chrome.tabs.sendMessage(activeTab.id, {"message": "create", "title": document.getElementById('title').value,
                                               "description": document.getElementById('description').value,
                                               "files": document.getElementById('files').value});
    });
}

function submissions() {
    //localStorage.setItem("text", "Convert your student's submissions directly into text!")
    document.getElementById('create').style.display = "none";
    document.getElementById('go').style.display = "flex";
    document.getElementById('text').style.display = "flex";
    document.getElementById('description').style.display = "none";
    document.getElementById('files').style.display = "none";
    document.getElementById('title').style.display = "none";
    document.getElementById('submissions').style.backgroundColor = "white";
    document.getElementById('submissions').style.color = "#f7965c";
    document.getElementById('assignments').style.color = "white";
    document.getElementById('assignments').style.backgroundColor = "#f7965c";

}

function assignments() {
    document.getElementById('text').style.display = "none";
    document.getElementById('description').style.display = "flex";
    document.getElementById('files').style.display = "flex";
    document.getElementById('title').style.display = "flex";
    document.getElementById('create').style.display = "flex";
    document.getElementById('go').style.display = "none";
    document.getElementById('assignments').style.backgroundColor = "white";
    document.getElementById('assignments').style.color = "#f7965c";
    document.getElementById('submissions').style.color = "white";
    document.getElementById('submissions').style.backgroundColor = "#f7965c";
}

document.addEventListener("DOMContentLoaded", function() {
    submissions();
    document.getElementById('go').addEventListener("click", go);
    document.getElementById('create').addEventListener("click", create);
    document.getElementById('assignments').addEventListener("click", assignments);
    document.getElementById('submissions').addEventListener("click", submissions);


    var text = localStorage.getItem("text");
    if (text === null) {
        document.getElementById('text').innerHTML = "Convert your student's submissions directly into text!";
    } else {
        document.getElementById('text').innerHTML = text;
    }
});

chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        if (request.message === "done") {
            localStorage.setItem("text", "Convert your student's submissions directly into text!");
            document.getElementById('text').innerHTML = "Complete!";
        }
    }
);
