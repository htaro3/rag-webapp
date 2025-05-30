import axios from 'axios';

// 型定義
interface FileInfo {
  filename: string;
  size: number;
  modified: number;
}

interface FileListResponse {
  files: FileInfo[];
}

interface DeleteFilesResponse {
  message: string;
  deleted_files: string[];
  failed_files: string[];
}

/**
 * アップロードされたファイル一覧を取得する
 */
export const getFiles = async (): Promise<FileListResponse> => {
  try {
    const response = await axios.get('/api/files');
    return response.data;
  } catch (error) {
    console.error('Error fetching files:', error);
    throw new Error('ファイル一覧の取得に失敗しました');
  }
};

/**
 * 特定のファイルの内容を取得する
 */
export const getFileContent = async (filename: string): Promise<string> => {
  try {
    const response = await axios.get(`/api/files/${filename}`, {
      responseType: 'text'
    });
    return response.data;
  } catch (error) {
    console.error(`Error fetching content for ${filename}:`, error);
    throw new Error('ファイル内容の取得に失敗しました');
  }
};

/**
 * 複数のファイルを削除する
 */
export const deleteFiles = async (filenames: string[]): Promise<DeleteFilesResponse> => {
  try {
    const response = await axios.delete('/api/files', {
      data: { filenames }
    });
    return response.data;
  } catch (error) {
    console.error('Error deleting files:', error);
    throw new Error('ファイルの削除に失敗しました');
  }
}; 