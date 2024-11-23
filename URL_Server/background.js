chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete') {
    try {
      const links = await extractLinksFromTab(tab.id);
      // Send links to server
      await sendLinksToServer(links);
      // Store in local storage
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
      files: ['contentScript.js']
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
      body: JSON.stringify({ links: links })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error sending links to server:', error);
    throw error;
  }
}