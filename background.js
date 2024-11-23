chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete') {
      const links = await extractLinksFromTab(tab.id);
      chrome.storage.local.set({ 'links': links });
    }
  });
  
  async function extractLinksFromTab(tabId) {
    return new Promise((resolve, reject) => {
      chrome.scripting.executeScript({
        target: { tabId: tabId },
        files: ['contentScript.js']  // Our content script that extracts links
      }, (results) => {
        if (chrome.runtime.lastError) {
          reject(chrome.runtime.lastError);
        } else {
          resolve(results[0].result.links);  // Assuming our content script returns { links }
        }
      });
    });
  }
  