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

// 集合管理功能
const loadCollections = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/collections`);
        const data = await response.json();
        const collectionsList = document.getElementById('collectionsList');
        const addCollectionSelect = document.getElementById('addCollectionSelect');
        const searchCollectionSelect = document.getElementById('searchCollectionSelect');

        // 更新集合列表
        collectionsList.innerHTML = data.collections.map(collection => `
            <div class="collection-item">
                <span>${collection}</span>
                <button class="delete-btn" onclick="deleteCollection('${collection}')">刪除</button>
            </div>
        `).join('');

        // 更新選擇器
        const options = data.collections.map(collection => 
            `<option value="${collection}">${collection}</option>`
        ).join('');
        addCollectionSelect.innerHTML = options;
        searchCollectionSelect.innerHTML = options;
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

const searchVectors = async (event) => {
    event.preventDefault();
    const collectionName = document.getElementById('searchCollectionSelect').value;
    const query = document.getElementById('searchQuery').value;
    const limit = parseInt(document.getElementById('searchLimit').value);

    try {
        const response = await fetch(`${API_BASE_URL}/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                collection_name: collectionName,
                query,
                limit
            })
        });

        const results = await response.json();
        displaySearchResults(results);
    } catch (error) {
        showNotification('搜索失敗', 'error');
    }
};

const displaySearchResults = (results) => {
    const resultsContainer = document.getElementById('searchResults');
    const resultsList = document.getElementById('resultsList');

    resultsContainer.classList.remove('hidden');
    resultsList.innerHTML = results.map(result => `
        <div class="result-item p-4 bg-gray-50 rounded-lg">
            <div class="font-medium">相似度: ${(result.score * 100).toFixed(2)}%</div>
            <div class="mt-2">${result.payload.text}</div>
        </div>
    `).join('');
};

// 事件監聽器
document.addEventListener('DOMContentLoaded', () => {
    loadCollections();
    document.getElementById('createCollectionForm').addEventListener('submit', createCollection);
    document.getElementById('addVectorForm').addEventListener('submit', addVector);
    document.getElementById('searchVectorForm').addEventListener('submit', searchVectors);
}); 