import "../css/main.scss";

// .js code goes here

if (typeof window.logErrorsLatch === "undefined") {
    // Probabilistic to avoid server overload. But log everything within
    // a single request for completeness
    window.logRequestLatch = Math.random() <= window.logConfig.requestLogProb;
    window.logErrorLatch = Math.random() <= window.logConfig.errorLogProb;
}

if (window.logErrorLatch) {
    window.addEventListener("error", function(e) {
        fetch(
            window.logConfig.errorPath,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    // Put these first in case of server truncation
                    "requestId": window.logConfig.requestId,
                    "file": e.filename,
                    "lineno": e.lineno,
                    "colno": e.colno,
                    "message": e.message,
                })
            }
        );
    }, false);
}

if (window.logRequestLatch) {
    window.addEventListener("load", function(e) {
        // Let the load event end before sending performance data, one
        // of the points is the loadEnd event.
        window.setTimeout(function() {
            if (!window.performance) return;
            var perf = window.performance.getEntriesByType("navigation")[0];

            fetch(
                window.logConfig.performancePath,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        "requestId": window.logConfig.requestId,
                        "domainLookupStart": perf.domainLookupStart,
                        "requestStart": perf.requestStart,
                        "responseStart": perf.responseStart,
                        "responseEnd": perf.responseEnd,
                        "loadEventEnd": perf.loadEventEnd,
                    })
                }
            );
        }, 1000);
    }, false);
}
