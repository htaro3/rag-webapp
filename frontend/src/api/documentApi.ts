import axios from 'axios';

interface UploadResponse {
  message: string;
}

/**
 * ドキュメントをアップロードする
 */
export const uploadDocument = async (file: File): Promise<UploadResponse> => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await axios.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('Error in uploadDocument:', error);
    throw new Error('ドキュメントのアップロード中にエラーが発生しました');
  }
}; 