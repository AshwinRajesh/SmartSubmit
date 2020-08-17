// content.js

chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        if (request.message === "create") {
            publish(sender, request.title, request.description, request.files.split("\n"));
            //assignmentClassName: A6dC2c bKJwEd VBEdtc-Wvd9Cc zZN2Lb-Wvd9Cc
        }
        if (request.message === "start") {
            convert(sender);
            //assignmentClassName: A6dC2c bKJwEd VBEdtc-Wvd9Cc zZN2Lb-Wvd9Cc
        }
    }
);

async function publish(sender, title, description, attachments) {
    var course = document.getElementById('UGb2Qe');
    var fileNames = {"files": []};
    for (var i = 0; i < attachments.length; i++) {
        if (!(fileNames['files'].includes(attachments[i].innerHTML))) {
            fileNames['files'].push(attachments[i]);
        }
    }
    fileNames = JSON.stringify(fileNames);
    await fetch("http://127.0.0.1:5000/publish?title=" + title + "&description=" + description + "&files=" + fileNames + "&course=" + course.innerHTML).then(r => r.text()).then(result => {
        console.log("Nice")
        chrome.runtime.sendMessage(sender.id, {"message": "done"});
	})

}

async function convert(sender){

    var course = document.getElementById("UGb2Qe");
    var assignment = document.getElementsByClassName("nk37z rUtoef")[0];

    await fetch("http://127.0.0.1:5000/generate_docs?course=" + course.innerHTML + "&assignment=" + assignment.innerHTML).then(r => r.text()).then(result => {
        console.log("Nice")
        chrome.runtime.sendMessage(sender.id, {"message": "done", "course": course.innerHTML, "assignment": assignment.innerHTML});
	})

}