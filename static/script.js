/* =====================================
   AI PDF ASSISTANT JAVASCRIPT
===================================== */


/* ELEMENTS */

const pdfInput = document.getElementById("pdfInput");
const uploadBtn = document.getElementById("uploadBtn");
const dropZone = document.getElementById("dropZone");

const chatContainer = document.getElementById("chatContainer");

const messageInput = document.getElementById("message");
const sendBtn = document.getElementById("sendBtn");

const typing = document.getElementById("typing");

const toast = document.getElementById("toast");

const pdfInfo = document.getElementById("pdfInfo");
const pdfName = document.getElementById("pdfName");
const charCount = document.getElementById("charCount");

const newChatBtn = document.getElementById("newChatBtn");


let selectedFile = null;


/* =====================================
   PDF SELECT
===================================== */


pdfInput.addEventListener(
    "change",
    function(){

        if(this.files.length > 0){

            selectedFile = this.files[0];

            showToast(
                "PDF selected: " + selectedFile.name
            );

        }

    }
);



/* =====================================
   DRAG AND DROP
===================================== */


dropZone.addEventListener(
    "dragover",
    (e)=>{

        e.preventDefault();

        dropZone.style.borderColor="#5B7CFF";

    }
);



dropZone.addEventListener(
    "dragleave",
    ()=>{

        dropZone.style.borderColor="";

    }
);



dropZone.addEventListener(
    "drop",
    (e)=>{

        e.preventDefault();


        if(e.dataTransfer.files.length){

            selectedFile=e.dataTransfer.files[0];

            showToast(
                "PDF selected: "+selectedFile.name
            );

        }

    }
);



/* =====================================
   UPLOAD PDF
===================================== */


uploadBtn.addEventListener(
    "click",
    uploadPDF
);



async function uploadPDF(){


    if(!selectedFile){

        showToast(
            "Please select a PDF first"
        );

        return;

    }



    let formData=new FormData();


    formData.append(
        "file",
        selectedFile
    );



    uploadBtn.innerText="Uploading...";


    try{


        let response=await fetch(
            "/upload",
            {

                method:"POST",

                body:formData

            }
        );



        let data=await response.json();



        if(data.success){


            pdfInfo.classList.remove(
                "hidden"
            );


            pdfName.innerText=data.filename;


            charCount.innerText=
            data.char_count+" characters";



            addMessage(
                "AI",
                "PDF uploaded successfully. You can ask questions about this document."
            );


            showToast(
                "PDF uploaded successfully"
            );


        }


        else{


            showToast(
                data.error
            );

        }


    }


    catch(error){


        showToast(
            "Upload failed"
        );


    }


    uploadBtn.innerText="Upload";


}



/* =====================================
   SEND MESSAGE
===================================== */


sendBtn.addEventListener(
    "click",
    sendMessage
);



messageInput.addEventListener(
    "keydown",
    function(e){


        if(e.key==="Enter" && !e.shiftKey){


            e.preventDefault();

            sendMessage();

        }


    }
);




async function sendMessage(){


    let message=
    messageInput.value.trim();



    if(!message){

        return;

    }



    addMessage(
        "User",
        message
    );


    messageInput.value="";



    showTyping();



    try{


        let response=await fetch(
            "/chat",
            {

                method:"POST",

                headers:{

                    "Content-Type":
                    "application/json"

                },


                body:JSON.stringify({

                    message:message

                })


            }
        );



        let data=
        await response.json();



        hideTyping();



        if(data.success){


            addMessage(
                "AI",
                data.response
            );


        }


        else{


            addMessage(
                "AI",
                data.error
            );


        }


    }


    catch(error){


        hideTyping();


        addMessage(
            "AI",
            "Something went wrong. Try again."
        );


    }


}



/* =====================================
   ADD CHAT MESSAGE
===================================== */


function addMessage(sender,text){


    let div=document.createElement(
        "div"
    );



    div.classList.add(
        "message"
    );



    if(sender==="User"){


        div.classList.add(
            "user-message"
        );


        div.innerHTML=

        `
        <span class="message-icon">
        👤
        </span>

        ${text}

        `;


    }


    else{


        div.classList.add(
            "ai-message"
        );


        div.innerHTML=

        `
        <span class="message-icon">
        🤖
        </span>

        ${text}

        `;


    }



    chatContainer.appendChild(
        div
    );



    chatContainer.scrollTop=
    chatContainer.scrollHeight;


}



/* =====================================
   TYPING
===================================== */


function showTyping(){

    typing.classList.remove(
        "hidden"
    );


    chatContainer.scrollTop=
    chatContainer.scrollHeight;

}



function hideTyping(){

    typing.classList.add(
        "hidden"
    );

}



/* =====================================
   TOAST
===================================== */


function showToast(message){


    toast.innerText=message;


    toast.classList.add(
        "show"
    );



    setTimeout(()=>{


        toast.classList.remove(
            "show"
        );


    },3000);


}



/* =====================================
   NEW CHAT
===================================== */


newChatBtn.addEventListener(
    "click",
    ()=>{


        chatContainer.innerHTML="";


        addMessage(
            "AI",
            "New chat started. Upload a PDF and ask questions."
        );


    }
);