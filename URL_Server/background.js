// URL_Server/background.js
// Track only the previous URL
let previousUrl = null;

chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete') {
        try {
            const links = await extractLinksFromTab(tabId);
            // Explicitly use string tokens '0' or '1'
            const token = (links.currentUrl === previousUrl) ? '1' : '0';
            
            // Update previous URL
            previousUrl = links.currentUrl;
            
            // Send links to the server with string token
            await sendLinksToServer(links, token);
            
            // Store the links in local storage (optional)
            chrome.storage.local.set({ 'links': links });
        } catch (error) {
            console.error('Error processing links:', error);
        }
    }
});

async function extractLinksFromTab(tabId) {
    return new Promise((resolve, reject) => {
        chrome.scripting.executeScript({
            target: { tabId: tabId },
            func: extractUrls
        }, (results) => {
            if (chrome.runtime.lastError) {
                reject(chrome.runtime.lastError);
            } else {
                resolve(results[0].result);
            }
        });
    });
}

async function sendLinksToServer(links, token) {
    try {
        const response = await fetch('http://localhost:5000/process-links', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                token: token,  // token is already a string '0' or '1'
                currentUrl: links.currentUrl, 
                allUrls: links.allUrls 
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log(data);
        return data;
    } catch (error) {
        console.error('Error sending links to server:', error);
        throw error;
    }
}

function extractUrls() {
    const linkElements = document.querySelectorAll('a');
    const urls = Array.from(linkElements)
        .map(a => a.href)
        .filter(url => url && url.startsWith('http'));

    return {
        currentUrl: window.location.href,
        allUrls: Array.from(new Set(urls))
    };
}