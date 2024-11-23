// URL_Server/background.js
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  // Check if the page has finished loading
  if (changeInfo.status === 'complete') {
    try {
      // Extract links from the current tab
      const links = await extractLinksFromTab(tabId);
      // Send links to the server
      await sendLinksToServer(links);
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

async function sendLinksToServer(links) {
  try {
    const response = await fetch('http://localhost:5000/process-links', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ currentUrl: links.currentUrl, allUrls: links.allUrls })
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

// Function to extract URLs from the page
function extractUrls() {
  const linkElements = document.querySelectorAll('a');
  const urls = Array.from(linkElements)
    .map(a => a.href)
    .filter(url => url && url.startsWith('http')); // Filter valid URLs only

  return {
    currentUrl: window.location.href,
    allUrls: Array.from(new Set(urls)) // Remove duplicates
  };
}
