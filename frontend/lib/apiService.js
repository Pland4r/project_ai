const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData
    });
    return await response.json();
  } catch (error) {
    console.error('Upload error:', error);
    throw error;
  }
};

export const analyzeData = async (filePath) => {
  try {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ file_path: filePath })
    });
    return await response.json();
  } catch (error) {
    console.error('Analysis error:', error);
    throw error;
  }
};
