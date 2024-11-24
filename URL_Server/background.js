let previousUrl = null;

console.log("Background script loaded");

// Function to check if a tabId is valid
async function isValidTab(tabId) {
    if (!tabId) return false;
    try {
        const tab = await chrome.tabs.get(tabId);
        return !!tab;
    } catch (error) {
        console.error('Error checking tab validity:', error);
        return false;
    }
}

// Function to process the current tab
async function processTab(tabId, url) {
    console.log('ProcessTab called with:', { tabId, url });
    
    try {
        // Early validation of tabId
        if (!tabId) {
            console.error('TabId is undefined or null');
            return;
        }

        // Verify tabId is valid
        const isValid = await isValidTab(tabId);
        if (!isValid) {
            console.error('Invalid tabId:', tabId);
            return;
        }

        console.log("Processing tab:", tabId, url);
        
        // Execute script to extract links
        const results = await chrome.scripting.executeScript({
            target: { tabId },
            function: function() {
                const links = Array.from(document.querySelectorAll('a'))
                    .map(a => a.href)
                    .filter(url => url && url.startsWith('http'));
                
                return {
                    currentUrl: window.location.href,
                    allUrls: Array.from(new Set(links))
                };
            }
        });

        if (!results?.[0]?.result) {
            throw new Error('Script execution failed to return results');
        }

        const result = results[0].result;
        const token = (result.currentUrl === previousUrl) ? '1' : '0';
        previousUrl = result.currentUrl;

        console.log("Extracted data:", {
            token,
            currentUrl: result.currentUrl,
            urlCount: result.allUrls.length
        });

        // Enhanced error handling for fetch
        try {
            const response = await fetch('http://127.0.0.1:50001/process-links', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Origin': chrome.runtime.getURL(''),
                },
                body: JSON.stringify({
                    token,
                    currentUrl: result.currentUrl,
                    allUrls: result.allUrls
                })
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Server error: ${response.status}. Details: ${errorText}`);
            }

            const responseData = await response.json();
            console.log("Server response:", responseData);

        } catch (fetchError) {
            console.error('Network or server error:', fetchError);
            throw fetchError;  // Re-throw to be caught by outer try-catch
        }

        console.log("Successfully processed page");

    } catch (error) {
        console.error('Error processing page:', error);
        console.error('Stack:', error.stack);
    }
}

// Listen for tab updates with additional checks
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
    console.log('Tab updated:', { tabId, changeInfo, url: tab?.url });
    
    if (changeInfo.status === 'complete' && tab?.url?.startsWith('http')) {
        try {
            // Verify tab still exists before processing
            const currentTab = await chrome.tabs.get(tabId);
            if (currentTab) {
                await processTab(tabId, currentTab.url);
            }
        } catch (error) {
            console.error('Error in onUpdated listener:', error);
        }
    }
});

// Listen for tab activation with additional checks
chrome.tabs.onActivated.addListener(async (activeInfo) => {
    console.log('Tab activated:', activeInfo);
    
    try {
        if (!activeInfo?.tabId) {
            console.error('No tabId in activeInfo:', activeInfo);
            return;
        }
        
        const tab = await chrome.tabs.get(activeInfo.tabId);
        if (tab?.url?.startsWith('http')) {
            await processTab(tab.id, tab.url);
        }
    } catch (error) {
        console.error('Error in onActivated listener:', error);
    }
});

// Initial processing of current tab when extension loads
async function initializeExtension() {
    console.log('Initializing extension...');
    
    try {
        const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
        console.log('Initial tabs:', tabs);
        
        if (tabs?.[0]?.id && tabs[0]?.url?.startsWith('http')) {
            await processTab(tabs[0].id, tabs[0].url);
        }
    } catch (error) {
        console.error('Error during initialization:', error);
    }
}

// Call initialization
initializeExtension();