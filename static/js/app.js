document.addEventListener("DOMContentLoaded", function() {
    // DOM Elements
    const sidebar = document.getElementById("sidebar");
    const toggleSidebarBtn = document.getElementById("toggle-sidebar");
    const podcastInput = document.getElementById("podcast-input");
    const generateBtn = document.getElementById("generate-btn");
    const loadingIndicator = document.getElementById("loading");
    const podcastResults = document.getElementById("podcast-results");
    const podcastResponses = document.getElementById("podcast-responses");
    const welcomeSection = document.getElementById("welcome-section");
    const historyList = document.getElementById("history-list");
    const emptyHistory = document.getElementById("empty-history");
    const clearHistoryBtn = document.getElementById("clear-history");
    
    // State
    let sidebarVisible = true;
    let podcastHistory = loadPodcastHistory();
    let conversationRound = 0;
    let conversationHistory = [];
    let isGenerating = false;
    
    // Initialize the app
    initApp();
    
    // Event Listeners
    toggleSidebarBtn.addEventListener("click", toggleSidebar);
    generateBtn.addEventListener("click", startPodcastGeneration);
    clearHistoryBtn.addEventListener("click", clearHistory);
    
    /**
     * Initializes the app by setting up the UI and loading history
     */
    function initApp() {
        renderHistoryList();
    }
    
    /**
     * Toggles the sidebar visibility
     */
    function toggleSidebar() {
        if (sidebarVisible) {
            sidebar.classList.add("-ml-64");
            sidebar.classList.remove("ml-0");
        } else {
            sidebar.classList.remove("-ml-64");
            sidebar.classList.add("ml-0");
        }
        sidebarVisible = !sidebarVisible;
    }
    
    /**
     * Starts the podcast generation process
     */
    function startPodcastGeneration() {
        const userPrompt = podcastInput.value.trim();
        
        if (!userPrompt) {
            alert("Please enter a topic or text for your podcast.");
            return;
        }
        
        if (isGenerating) {
            return; // Prevent multiple generations
        }
        
        // Reset conversation state
        conversationRound = 0;
        conversationHistory = [];
        isGenerating = true;
        
        // Show loading indicator and hide other sections
        loadingIndicator.classList.remove("hidden");
        welcomeSection.classList.add("hidden");
        podcastResults.classList.add("hidden");
        
        // Clear previous results
        podcastResponses.innerHTML = "";
        
        // Add user prompt to UI
        podcastResponses.innerHTML += `
            <div class="mb-6 fade-in">
                <h3 class="font-semibold text-gray-700">Podcast Topic:</h3>
                <div class="bg-gray-100 p-4 rounded-lg mt-2 border border-gray-200">
                    <p class="text-gray-800">${escapeHTML(userPrompt)}</p>
                </div>
            </div>
            <div class="mb-4">
                <h3 class="font-semibold text-gray-700 flex items-center">
                    <i class="fas fa-comments text-primary-500 mr-2"></i>
                    AI Podcast Conversation:
                </h3>
            </div>
        `;
        
        // Start the conversation loop
        generatePodcast(userPrompt);
    }
    
    /**
     * Generates a podcast round based on user input and previous conversation
     * @param {string} userPrompt - The user's topic
     */
    function generatePodcast(userPrompt) {
        // Disable generate button
        generateBtn.disabled = true;
        generateBtn.classList.add("opacity-50");
        
        // Update loading message
        const loadingMessage = document.querySelector("#loading span");
        if (loadingMessage) {
            loadingMessage.textContent = `Generating podcast round ${conversationRound + 1} of 3...`;
        }
        
        // Prepare the payload for the API
        let payload = { user: userPrompt };
        
        // For rounds after the first, include previous LLM responses
        if (conversationRound > 0) {
            // Format previous responses for context
            let conversationContext = `We're having a podcast discussion about "${userPrompt}". `;
            conversationContext += "Please continue the conversation by responding to what others have said so far.\n\n";
            
            // Add each previous round of conversation
            conversationHistory.forEach((round, index) => {
                conversationContext += `--- Round ${index + 1} ---\n`;
                Object.entries(round).forEach(([model, response]) => {
                    // Use display names instead of model IDs
                    const displayName = getModelDisplayName(model);
                    conversationContext += `${displayName}: ${response}\n\n`;
                });
            });
            
            // Set the enhanced prompt with conversation history
            payload.user = conversationContext;
        }
        
        // Call API
        fetch("/podcast", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then(data => {
            // Process and store this round of conversation
            if (data.data && data.data.length > 0) {
                const roundResponses = data.data[0];
                conversationHistory.push(roundResponses);
                
                // Display this round of conversation
                displayConversationRound(roundResponses, conversationRound + 1);
                
                // Increment the round counter
                conversationRound++;
                
                // Continue to next round or finish
                if (conversationRound < 3) {
                    // Show results section if not already visible
                    if (podcastResults.classList.contains("hidden")) {
                        podcastResults.classList.remove("hidden");
                    }
                    
                    // Short delay before next round to make it feel more natural
                    setTimeout(() => {
                        generatePodcast(userPrompt);
                    }, 1000);
                } else {
                    // All rounds complete, save to history
                    finalizePodcast(userPrompt);
                }
            } else {
                throw new Error("No podcast responses were generated");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            podcastResponses.innerHTML += `
                <div class="bg-red-100 text-red-700 p-4 rounded-lg mb-4 fade-in">
                    <h3 class="font-bold">Error</h3>
                    <p>${error.message}</p>
                </div>
            `;
            finalizePodcast(userPrompt);
        });
    }
    
    /**
     * Displays a single round of conversation in the UI
     * @param {Object} roundData - The LLM responses for this round
     * @param {number} roundNumber - The conversation round number
     */
    function displayConversationRound(roundData, roundNumber) {
        const roundContainer = document.createElement("div");
        roundContainer.className = "mb-8 fade-in podcast-round";
        roundContainer.setAttribute("data-round", roundNumber);
        
        // Round header
        roundContainer.innerHTML = `
            <div class="flex items-center mb-3">
                <div class="bg-primary-600 text-white rounded-full w-6 h-6 flex items-center justify-center mr-2">
                    <span class="text-xs font-bold">${roundNumber}</span>
                </div>
                <h4 class="text-sm font-medium text-gray-500">Round ${roundNumber}</h4>
            </div>
        `;
        
        // Model responses in this round
        const modelColors = {
            "deepseek-chat": "bg-blue-50 border-blue-200 text-blue-800",
            "chatgpt-4o-latest": "bg-green-50 border-green-200 text-green-800",
            "google/gemini-2.0-flash": "bg-purple-50 border-purple-200 text-purple-800",
            "x-ai/grok-3-beta": "bg-orange-50 border-orange-200 text-orange-800",
            "claude-3-sonnet-20240229": "bg-indigo-50 border-indigo-200 text-indigo-800",
            "gpt-4o": "bg-teal-50 border-teal-200 text-teal-800"
        };
        
        // Custom ordering to make conversation flow better
        const modelOrder = [
            "gpt-4o", 
            "claude-3-sonnet-20240229", 
            "deepseek-chat", 
            "google/gemini-2.0-flash",
            "chatgpt-4o-latest", 
            "x-ai/grok-3-beta"
        ];
        
        // Sort the models to ensure a consistent conversation flow
        const sortedModels = Object.keys(roundData).sort((a, b) => {
            return modelOrder.indexOf(a) - modelOrder.indexOf(b);
        });
        
        // Add each model's response to this round
        sortedModels.forEach(model => {
            const response = roundData[model];
            const colorClass = modelColors[model] || "bg-gray-50 border-gray-200 text-gray-800";
            const displayName = getModelDisplayName(model);
            
            roundContainer.innerHTML += `
                <div class="podcast-message ${colorClass} mb-4 border rounded-lg shadow-sm overflow-hidden">
                    <div class="flex items-center px-4 py-2 bg-white border-b border-gray-100">
                        <i class="fas fa-robot mr-2 text-primary-500"></i>
                        <span class="font-medium">${displayName}</span>
                    </div>
                    <div class="px-4 py-3">
                        <p>${formatResponse(response)}</p>
                    </div>
                </div>
            `;
        });
        
        // Add this round to the UI
        podcastResponses.appendChild(roundContainer);
        
        // Scroll to the newest content
        roundContainer.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
    
    /**
     * Finalizes the podcast generation process
     * @param {string} userPrompt - The original user prompt
     */
    function finalizePodcast(userPrompt) {
        // Hide loading indicator
        loadingIndicator.classList.add("hidden");
        
        // Enable generate button
        generateBtn.disabled = false;
        generateBtn.classList.remove("opacity-50");
        
        // Reset generation flag
        isGenerating = false;
        
        // Save to history if we have responses
        if (conversationHistory.length > 0) {
            const podcastId = Date.now().toString();
            const historyItem = {
                id: podcastId,
                prompt: userPrompt,
                responses: conversationHistory,
                timestamp: new Date().toISOString()
            };
            
            savePodcastToHistory(historyItem);
            renderHistoryList();
        }
        
        // Show results section
        podcastResults.classList.remove("hidden");
    }
    
    /**
     * Gets a display name for an AI model
     * @param {string} model - The model identifier
     * @returns {string} - User-friendly display name
     */
    function getModelDisplayName(model) {
        const modelNames = {
            "deepseek-chat": "DeepSeek",
            "chatgpt-4o-latest": "ChatGPT",
            "google/gemini-2.0-flash": "Gemini",
            "x-ai/grok-3-beta": "Grok",
            "claude-3-sonnet-20240229": "Claude",
            "gpt-4o": "GPT-4o"
        };
        
        return modelNames[model] || model;
    }
    
    /**
     * Formats API response text with line breaks
     * @param {string} text - The response text
     * @returns {string} - Formatted HTML
     */
    function formatResponse(text) {
        if (!text) return "<em>No response</em>";
        return escapeHTML(text)
            .replace(/\n\n/g, "</p><p>")
            .replace(/\n/g, "<br>");
    }
    
    /**
     * Escapes HTML special characters
     * @param {string} text - Text to escape
     * @returns {string} - Escaped text
     */
    function escapeHTML(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Loads podcast history from local storage
     * @returns {Array} - Array of podcast history items
     */
    function loadPodcastHistory() {
        try {
            const history = localStorage.getItem("podcastHistory");
            return history ? JSON.parse(history) : [];
        } catch (error) {
            console.error("Error loading history:", error);
            return [];
        }
    }
    
    /**
     * Saves a podcast to history
     * @param {Object} podcast - The podcast to save
     */
    function savePodcastToHistory(podcast) {
        try {
            podcastHistory.unshift(podcast);
            localStorage.setItem("podcastHistory", JSON.stringify(podcastHistory));
        } catch (error) {
            console.error("Error saving podcast to history:", error);
        }
    }
    
    /**
     * Renders the history list in the sidebar
     */
    function renderHistoryList() {
        // Clear the list except for the empty history message
        historyList.innerHTML = "";
        historyList.appendChild(emptyHistory);
        
        if (podcastHistory.length === 0) {
            emptyHistory.classList.remove("hidden");
            return;
        }
        
        emptyHistory.classList.add("hidden");
        
        podcastHistory.forEach(item => {
            const date = new Date(item.timestamp);
            const formattedDate = date.toLocaleDateString() + " " + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            
            const historyItem = document.createElement("div");
            historyItem.className = "p-3 hover:bg-primary-700 cursor-pointer border-b border-primary-700";
            historyItem.innerHTML = `
                <div class="text-sm font-semibold truncate">${escapeHTML(item.prompt.substring(0, 50))}</div>
                <div class="text-xs text-primary-300">${formattedDate}</div>
            `;
            
            historyItem.addEventListener("click", () => {
                displayHistoryItem(item);
            });
            
            historyList.appendChild(historyItem);
        });
    }
    
    /**
     * Displays a history item in the main content area
     * @param {Object} item - The history item to display
     */
    function displayHistoryItem(item) {
        welcomeSection.classList.add("hidden");
        loadingIndicator.classList.add("hidden");
        
        // Add user prompt to UI
        podcastResponses.innerHTML = `
            <div class="mb-6 fade-in">
                <h3 class="font-semibold text-gray-700">Podcast Topic:</h3>
                <div class="bg-gray-100 p-4 rounded-lg mt-2 border border-gray-200">
                    <p class="text-gray-800">${escapeHTML(item.prompt)}</p>
                </div>
            </div>
            <div class="mb-4">
                <h3 class="font-semibold text-gray-700 flex items-center">
                    <i class="fas fa-comments text-primary-500 mr-2"></i>
                    AI Podcast Conversation:
                </h3>
            </div>
        `;
        
        // Display each round of the conversation
        if (Array.isArray(item.responses)) {
            item.responses.forEach((roundData, index) => {
                displayConversationRound(roundData, index + 1);
            });
        } else {
            // Backward compatibility for old format
            displayConversationRound(item.responses, 1);
        }
        
        // Show results
        podcastResults.classList.remove("hidden");
        
        // If sidebar is visible and on mobile, hide it
        if (sidebarVisible && window.innerWidth < 768) {
            toggleSidebar();
        }
    }
    
    /**
     * Clears all podcast history
     */
    function clearHistory() {
        if (confirm("Are you sure you want to clear all podcast history?")) {
            podcastHistory = [];
            localStorage.removeItem("podcastHistory");
            renderHistoryList();
        }
    }
}); 