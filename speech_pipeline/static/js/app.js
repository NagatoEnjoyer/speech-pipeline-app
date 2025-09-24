document.getElementById("uploadForm").addEventListener("submit", function(e) {
    e.preventDefault();
    const fileInput = document.getElementById("fileInput");
    if (!fileInput.files.length) return alert("Válassz fájlt!");

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    fetch("/upload", { method: "POST", body: formData })
        .then(response => response.json())
        .then(data => {
            if (data.task_id) pollStatus(data.task_id);
        });
});

function pollStatus(task_id) {
    const statusText = document.getElementById("statusText");
    const spinner = document.getElementById("spinner");

    spinner.style.display = "inline-block";

    const interval = setInterval(() => {
        fetch(`/status/${task_id}`)
            .then(resp => resp.json())
            .then(data => {
                let result = data.result;
                    if (typeof result === "string") {
                        result = {summary: result, download_file: "downloadFileName.txt"};
                    }
                if (data.status === "done") {
                    clearInterval(interval);
                    document.getElementById("status").innerText = "Feldolgozás kész ✅";
                    document.getElementById("summary").innerText = result.summary;
                    const downloadBtn = document.getElementById("downloadBtn");
                    downloadBtn.style.display = "block";
                    downloadBtn.onclick = () => {
                        window.location.href = `/download/${result.download_file}`;
                    };

                    document.getElementById("translator").style.display = "block";
                } else if (data.status === "failed") {
                    clearInterval(interval);
                    statusText.innerText = "Hiba a feldolgozás során: " + data.result;
                    spinner.style.display = "none";
                } else {
                    statusText.innerText = "Feldolgozás alatt...";
                    spinner.style.display = "inline-block";
                }
            });
    }, 2000);
}

function queueTranslate() {
    const sourceLang = document.getElementById("sourceLang").value;
    const targetLang = document.getElementById("targetLang").value;
    const text = document.getElementById("summary").innerText;
    const statusText = document.getElementById("translationStatus");
    const spinner = document.getElementById("spinnerTranslation");
    const downloadTranslationBtn = document.getElementById("downloadTranslationBtn");

    statusText.innerText = "Fordítás alatt...";
    spinner.style.display = "inline-block";

    fetch("/translate_queue", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            text: text,
            source_lang: sourceLang,
            target_lang: targetLang
        })
    })
        .then(resp => resp.json())
        .then(data => {

            if (data.task_id) {
                const interval = setInterval(() => {
                    fetch(`/status/${data.task_id}`)
                        .then(r => r.json())
                        .then(taskData => {
                            let result = taskData.result;
                            if (typeof result === "string") {
                                result = {translated_text: result, download_file: "downloadFileName.txt"};
                            }

                            if (taskData.status === "done") {
                                clearInterval(interval);
                                spinner.style.display = "none";
                                statusText.innerText = "Fordítás kész";
                                document.getElementById("translationResult").innerText = result.translated_text;
                                downloadTranslationBtn.style.display = "block";
                                downloadTranslationBtn.onclick = () => {
                                    window.location.href = `/download/${result.download_file}`;
                                };
                            } else if (taskData.status === "failed") {
                                clearInterval(interval)
                                spinner.style.display = "none";
                                statusText.innerText = "Fordítási hiba";
                                document.getElementById("translationResult").innerText = "Fordítás hiba: " + data.error;
                            } else {
                                statusText.innerText = "Fordítás alatt...";
                            }
                        });
                }, 2000);
            }
        });
}
    //     spinner.style.display = "none";
    //     if (data.translated_text) {
    //         statusText.innerText = "Fordítás kész ✅";
    //         document.getElementById("translationResult").innerText = data.translated_text;
    //         downloadTranslationBtn.style.display = "block";
    //         downloadTranslationBtn.onclick = () => {
    //             window.location.href = `/download/${data.download_file}`;
    //         };
    //     } else {
    //         statusText.innerText = "Fordítási hiba ❌";
    //         document.getElementById("translationResult").innerText = "Fordítás hiba: " + data.error;
    //     }
    // })
//     .catch(err => {
//         spinner.style.display = "none";
//         statusText.innerText = "Fordítás sikertelen ❌";
//         console.error("Fordítás hiba:", err);
//         document.getElementById("translationResult").innerText = "Fordítás sikertelen.";
//     });
// }