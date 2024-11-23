document.addEventListener('DOMContentLoaded', function() {
    // Fetch data from the server
    fetch('http://localhost:5000/send-links')
      .then(response => response.json())  // Parse the JSON response
      .then(data => {
        const linksContainer = document.getElementById('links');
        const activeTabUrl = document.getElementById('activeTabUrl');
        const links = data.links || [];  // Get the links array from the response
  
        // If links are found, display them
        if (links.length > 0) {
          activeTabUrl.textContent = 'Active Tab URL: ' + links[0]; // Display the first link (active tab)
          links.slice(1).forEach(link => {
            const linkElement = document.createElement('a');
            linkElement.href = link;
            linkElement.classList.add('link');
            linkElement.textContent = link;
            linkElement.target = '_blank'; // Open link in a new tab
            linksContainer.appendChild(linkElement);
          });
        } else {
          activeTabUrl.textContent = 'No links found.';  // Display a fallback message
        }
      })
      .catch(error => {
        console.error('Error fetching links from server:', error);  // Log any errors
      });
  });
  