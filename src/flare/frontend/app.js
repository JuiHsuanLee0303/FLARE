// API 端點配置
const API_BASE_URL = 'http://localhost:8000';

// 工具函數
const showNotification = (message, type = 'success') => {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    } text-white fade-in`;
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
};

// 格式化時間戳
const formatTimestamp = () => {
    const now = new Date();
    return now.toLocaleTimeString('zh-TW', { 
        hour: '2-digit', 
        minute: '2-digit'
    });
};

// 添加聊天消息
const addChatMessage = (message, isUser = false) => {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${isUser ? 'user' : 'bot'}`;
    
    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = message;
    
    const timestamp = document.createElement('div');
    timestamp.className = 'timestamp';
    timestamp.textContent = formatTimestamp();
    
    messageDiv.appendChild(content);
    messageDiv.appendChild(timestamp);
    chatMessages.appendChild(messageDiv);
    
    // 滾動到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;
};

// 處理聊天
const handleChat = async (event) => {
    event.preventDefault();
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();
    const collectionName = document.getElementById('searchCollectionSelect').value || 'test1';
    const limit = parseInt(document.getElementById('searchLimit').value) || 10;
    
    if (!message) return;
    
    // 顯示用戶消息
    addChatMessage(message, true);
    chatInput.value = '';
    
    try {
        // 發送消息到後端
        const response = await fetch(`${API_BASE_URL}/chat?prompt=${message}&collection_name=${collectionName}&limit=${limit}`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                prompt: message,
                collection_name: collectionName,
                limit: limit
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            console.error('聊天錯誤響應:', errorData);
            throw new Error(errorData.detail || '聊天請求失敗');
        }
        
        const data = await response.json();
        console.log('聊天響應:', data);
        
        // 顯示機器人回應
        addChatMessage(data.response || data.message || '抱歉，我無法理解您的問題。', false);
    } catch (error) {
        console.error('聊天錯誤:', error);
        showNotification('聊天請求失敗', 'error');
        addChatMessage('抱歉，我現在無法回應您的問題。請稍後再試。', false);
    }
};

// 文件上傳功能
const handleFileUpload = async (event) => {
    event.preventDefault();
    const fileInput = document.getElementById('fileInput');
    const collectionName = document.getElementById('uploadCollectionSelect').value;
    const chunkSize = parseInt(document.getElementById('chunkSize').value);
    const chunkOverlap = parseInt(document.getElementById('chunkOverlap').value);

    if (!fileInput.files.length) {
        showNotification('請選擇文件', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('collection_name', collectionName);
    formData.append('chunk_size', chunkSize);
    formData.append('chunk_overlap', chunkOverlap);

    try {
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('上傳失敗');
        }

        const data = await response.json();
        showNotification('文件上傳成功');
        fileInput.value = '';
    } catch (error) {
        console.error('上傳錯誤:', error);
        showNotification('文件上傳失敗', 'error');
    }
};

// 獲取集合信息
const getCollectionInfo = async (collectionName) => {
    try {
        const response = await fetch(`${API_BASE_URL}/collection/${collectionName}/info`);
        if (!response.ok) {
            throw new Error('獲取信息失敗');
        }

        const info = await response.json();
        const infoContainer = document.getElementById('collectionInfo');
        const infoContent = document.getElementById('infoContent');

        infoContainer.classList.remove('hidden');
        infoContent.innerHTML = `
            <div class="grid grid-cols-2 gap-4">
                <div class="p-4 bg-gray-50 rounded-lg">
                    <h3 class="font-medium text-gray-700">集合名稱</h3>
                    <p class="mt-2">${collectionName}</p>
                </div>
                <div class="p-4 bg-gray-50 rounded-lg">
                    <h3 class="font-medium text-gray-700">向量數量</h3>
                    <p class="mt-2">${info.vectors_count || 0}</p>
                </div>
                <div class="p-4 bg-gray-50 rounded-lg">
                    <h3 class="font-medium text-gray-700">向量大小</h3>
                    <p class="mt-2">${info.config.params.vectors.size}</p>
                </div>
                <div class="p-4 bg-gray-50 rounded-lg">
                    <h3 class="font-medium text-gray-700">距離度量</h3>
                    <p class="mt-2">${info.config.params.vectors.distance}</p>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('獲取集合信息錯誤:', error);
        showNotification('獲取集合信息失敗', 'error');
    }
};

// 集合管理功能
const loadCollections = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/collections`);
        const data = await response.json();
        const collectionsList = document.getElementById('collectionsList');
        const addCollectionSelect = document.getElementById('addCollectionSelect');
        const searchCollectionSelect = document.getElementById('searchCollectionSelect');
        const uploadCollectionSelect = document.getElementById('uploadCollectionSelect');

        // 更新集合列表
        collectionsList.innerHTML = data.collections.map(collection => `
            <div class="collection-item">
                <div class="flex items-center space-x-2">
                    <span>${collection}</span>
                    <button class="text-blue-500 hover:text-blue-600" onclick="getCollectionInfo('${collection}')">
                        <i class="fas fa-info-circle"></i>
                    </button>
                </div>
                <button class="delete-btn" onclick="deleteCollection('${collection}')">刪除</button>
            </div>
        `).join('');

        // 更新選擇器
        const options = data.collections.map(collection => 
            `<option value="${collection}">${collection}</option>`
        ).join('');
        addCollectionSelect.innerHTML = options;
        searchCollectionSelect.innerHTML = options;
        uploadCollectionSelect.innerHTML = options;
    } catch (error) {
        showNotification('載入集合失敗', 'error');
    }
};

const createCollection = async (event) => {
    event.preventDefault();
    const name = document.getElementById('collectionName').value;
    const vectorSize = parseInt(document.getElementById('vectorSize').value);
    const distance = document.getElementById('distance').value;

    try {
        const response = await fetch(`${API_BASE_URL}/collection/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ collection_name: name, vector_size: vectorSize, distance })
        });

        if (response.ok) {
            showNotification('集合創建成功');
            loadCollections();
            event.target.reset();
        } else {
            throw new Error('創建失敗');
        }
    } catch (error) {
        showNotification('創建集合失敗', 'error');
    }
};

const deleteCollection = async (collectionName) => {
    if (!confirm(`確定要刪除集合 ${collectionName} 嗎？`)) return;

    try {
        const response = await fetch(`${API_BASE_URL}/collection/${collectionName}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showNotification('集合刪除成功');
            loadCollections();
        } else {
            throw new Error('刪除失敗');
        }
    } catch (error) {
        showNotification('刪除集合失敗', 'error');
    }
};

// 向量操作功能
const addVector = async (event) => {
    event.preventDefault();
    const collectionName = document.getElementById('addCollectionSelect').value;
    const chunk = document.getElementById('chunkText').value;

    try {
        const response = await fetch(`${API_BASE_URL}/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                collection_name: collectionName,
                chunk,
                payloads: [{ source: 'web' }]
            })
        });

        if (response.ok) {
            showNotification('向量添加成功');
            event.target.reset();
        } else {
            throw new Error('添加失敗');
        }
    } catch (error) {
        showNotification('添加向量失敗', 'error');
    }
};

// 搜索向量
const searchVectors = async (event) => {
    event.preventDefault();
    const collectionName = document.getElementById('searchCollectionSelect').value;
    const query = document.getElementById('searchQuery').value;
    const limit = parseInt(document.getElementById('searchLimit').value) || 10;

    console.log('搜索參數:', {
        collection_name: collectionName,
        query: query,
        limit: limit
    });

    if (!collectionName || !query) {
        showNotification('請填寫所有必要欄位', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/search`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                collection_name: collectionName,
                query: query,
                limit: limit
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('搜索錯誤響應:', errorData);
            throw new Error(errorData.detail || '搜索失敗');
        }

        const results = await response.json();
        console.log('搜索結果:', results);
        displaySearchResults(results);
    } catch (error) {
        console.error('搜索錯誤:', error);
        showNotification(error.message || '搜索失敗', 'error');
    }
};

const displaySearchResults = (results) => {
    const resultsContainer = document.getElementById('searchResults');
    const resultsList = document.getElementById('resultsList');

    resultsContainer.classList.remove('hidden');
    
    if (!results || results.length === 0) {
        resultsList.innerHTML = '<div class="text-gray-500 text-center py-4">沒有找到相關結果</div>';
        return;
    }

    resultsList.innerHTML = results.map(result => `
        <div class="result-item p-4 bg-gray-50 rounded-lg">
            <div class="font-medium">相似度: ${(result.score * 100).toFixed(2)}%</div>
            <div class="mt-2">${result.payload?.text || '無內容'}</div>
        </div>
    `).join('');
};

// 事件監聽器
document.addEventListener('DOMContentLoaded', () => {
    loadCollections();
    document.getElementById('createCollectionForm').addEventListener('submit', createCollection);
    document.getElementById('addVectorForm').addEventListener('submit', addVector);
    document.getElementById('searchVectorForm').addEventListener('submit', searchVectors);
    document.getElementById('chatForm').addEventListener('submit', handleChat);
    document.getElementById('uploadForm').addEventListener('submit', handleFileUpload);
    
    // 添加歡迎消息
    addChatMessage('您好！我是 FLARE RAG 系統的助手。請問有什麼我可以幫您的嗎？', false);
}); 