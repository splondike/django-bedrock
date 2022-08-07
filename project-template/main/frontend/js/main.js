// .js code goes here

window.addEventListener("error", function(e) {
    // Probabilistic to avoid server overload. But log everything within
    // a single request for completeness
    if (typeof window.logErrorsLatch === "undefined") {
        window.logErrorsLatch = Math.random() <= window.logConfig.errorLogProb;
    }

    if (window.logErrorsLatch) {
        fetch(
            window.logConfig.errorPath,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    // Put these first in case of server truncation
                    "file": e.filename,
                    "lineno": e.lineno,
                    "colno": e.colno,
                    "message": e.message,
                })
            }
        );
    }
}, false);
