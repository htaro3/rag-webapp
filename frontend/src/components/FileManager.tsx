import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { getFiles, getFileContent, deleteFiles } from '../api/fileApi';

// 型定義
interface FileInfo {
  filename: string;
  size: number;
  modified: number;
}

// スタイル定義
const FileManagerContainer = styled.div`
  margin-bottom: 2rem;
`;

const FileTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
  background-color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
`;

const Th = styled.th`
  text-align: left;
  padding: 0.75rem 1rem;
  border-bottom: 2px solid #f0f0f0;
  color: #616161;
  font-weight: 500;
`;

const Td = styled.td`
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f0f0f0;
  vertical-align: middle;
`;

const CheckboxCell = styled(Td)`
  width: 48px;
`;

const ActionBar = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
`;

const SearchInput = styled.input`
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  min-width: 250px;
`;

const Button = styled.button`
  padding: 0.5rem 1rem;
  background-color: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  
  &:hover {
    background-color: #1976d2;
  }
  
  &:disabled {
    background-color: #bdbdbd;
    cursor: not-allowed;
  }
`;

const DeleteButton = styled(Button)`
  background-color: #f44336;
  
  &:hover {
    background-color: #d32f2f;
  }
`;

const FileRow = styled.tr<{ isSelected: boolean }>`
  background-color: ${props => props.isSelected ? 'rgba(33, 150, 243, 0.05)' : 'transparent'};
  cursor: pointer;
  
  &:hover {
    background-color: ${props => props.isSelected ? 'rgba(33, 150, 243, 0.1)' : 'rgba(0, 0, 0, 0.02)'};
  }
`;

const FileNameCell = styled(Td)`
  cursor: pointer;
  color: #1976d2;
  
  &:hover {
    text-decoration: underline;
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 2rem;
  color: #757575;
`;

const Modal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background-color: white;
  padding: 2rem;
  border-radius: 4px;
  max-width: 80%;
  max-height: 80%;
  overflow: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  position: relative;
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #f0f0f0;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #757575;
  
  &:hover {
    color: #212121;
  }
`;

const FileContent = styled.pre`
  white-space: pre-wrap;
  font-family: monospace;
  margin: 0;
  padding: 1rem;
  background-color: #f9f9f9;
  border-radius: 4px;
  max-height: 60vh;
  overflow-y: auto;
`;

const Message = styled.div<{ isError?: boolean }>`
  padding: 1rem;
  margin-top: 1rem;
  border-radius: 4px;
  background-color: ${props => props.isError ? '#ffebee' : '#e8f5e9'};
  color: ${props => props.isError ? '#c62828' : '#2e7d32'};
  border-left: 4px solid ${props => props.isError ? '#c62828' : '#2e7d32'};
`;

const FileManager: React.FC = () => {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // モーダル表示用の状態
  const [modalOpen, setModalOpen] = useState(false);
  const [currentFile, setCurrentFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [contentLoading, setContentLoading] = useState(false);

  // ファイル一覧の取得
  const fetchFiles = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await getFiles();
      setFiles(data.files);
    } catch (err) {
      console.error('Error fetching files:', err);
      setError('ファイル一覧の取得に失敗しました');
    } finally {
      setIsLoading(false);
    }
  };
  
  // コンポーネントマウント時にファイル一覧を取得
  useEffect(() => {
    fetchFiles();
  }, []);

  // ファイル選択の切り替え
  const toggleFileSelection = (filename: string) => {
    setSelectedFiles(prev => 
      prev.includes(filename) 
        ? prev.filter(file => file !== filename) 
        : [...prev, filename]
    );
  };
  
  // すべてのファイルを選択/解除
  const toggleSelectAll = () => {
    if (selectedFiles.length === filteredFiles.length) {
      setSelectedFiles([]);
    } else {
      setSelectedFiles(filteredFiles.map(file => file.filename));
    }
  };
  
  // ファイルの削除
  const handleDelete = async () => {
    if (selectedFiles.length === 0) return;
    
    if (!window.confirm(`${selectedFiles.length}個のファイルを削除しますか？`)) {
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      const result = await deleteFiles(selectedFiles);
      setSuccess(result.message);
      setSelectedFiles([]);
      fetchFiles(); // 一覧を再取得
    } catch (err) {
      console.error('Error deleting files:', err);
      setError('ファイルの削除に失敗しました');
    } finally {
      setIsLoading(false);
    }
  };
  
  // ファイルコンテンツの表示
  const viewFileContent = async (filename: string) => {
    setCurrentFile(filename);
    setModalOpen(true);
    setContentLoading(true);
    
    try {
      const content = await getFileContent(filename);
      setFileContent(content);
    } catch (err) {
      console.error('Error loading file content:', err);
      setFileContent('ファイル内容の読み込みに失敗しました');
    } finally {
      setContentLoading(false);
    }
  };
  
  // 検索フィルタリング
  const filteredFiles = searchTerm
    ? files.filter(file => 
        file.filename.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : files;

  // サイズを人間が読みやすい形式に変換
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };
  
  // 日付をフォーマット
  const formatDate = (timestamp: number): string => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  return (
    <FileManagerContainer>
      <h2>ファイル管理</h2>
      <p>アップロードしたテキストファイルの管理とコンテンツの閲覧ができます。</p>
      
      <ActionBar>
        <SearchInput 
          type="text" 
          placeholder="ファイル名で検索..." 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <div>
          <DeleteButton 
            onClick={handleDelete} 
            disabled={selectedFiles.length === 0 || isLoading}
          >
            {selectedFiles.length > 0 
              ? `選択したファイルを削除 (${selectedFiles.length})` 
              : 'ファイルを選択'
            }
          </DeleteButton>
          <Button 
            onClick={fetchFiles}
            disabled={isLoading}
            style={{ marginLeft: '0.5rem' }}
          >
            更新
          </Button>
        </div>
      </ActionBar>
      
      {error && <Message isError={true}>{error}</Message>}
      {success && <Message>{success}</Message>}
      
      {files.length === 0 ? (
        <EmptyState>
          {isLoading ? 'ファイル一覧を読み込み中...' : 'アップロードされたファイルがありません'}
        </EmptyState>
      ) : (
        <FileTable>
          <thead>
            <tr>
              <CheckboxCell>
                <input 
                  type="checkbox" 
                  checked={selectedFiles.length === filteredFiles.length && filteredFiles.length > 0}
                  onChange={toggleSelectAll}
                />
              </CheckboxCell>
              <Th>ファイル名</Th>
              <Th>サイズ</Th>
              <Th>更新日時</Th>
            </tr>
          </thead>
          <tbody>
            {filteredFiles.map((file) => (
              <FileRow 
                key={file.filename}
                isSelected={selectedFiles.includes(file.filename)}
                onClick={() => toggleFileSelection(file.filename)}
              >
                <CheckboxCell onClick={(e) => e.stopPropagation()}>
                  <input 
                    type="checkbox" 
                    checked={selectedFiles.includes(file.filename)}
                    onChange={() => toggleFileSelection(file.filename)}
                  />
                </CheckboxCell>
                <FileNameCell 
                  onClick={(e) => {
                    e.stopPropagation();
                    viewFileContent(file.filename);
                  }}
                >
                  {file.filename}
                </FileNameCell>
                <Td>{formatFileSize(file.size)}</Td>
                <Td>{formatDate(file.modified)}</Td>
              </FileRow>
            ))}
          </tbody>
        </FileTable>
      )}
      
      {/* ファイルコンテンツ表示モーダル */}
      {modalOpen && (
        <Modal onClick={() => setModalOpen(false)}>
          <ModalContent onClick={(e) => e.stopPropagation()}>
            <ModalHeader>
              <h3>{currentFile}</h3>
              <CloseButton onClick={() => setModalOpen(false)}>×</CloseButton>
            </ModalHeader>
            {contentLoading ? (
              <div className="loading-spinner" />
            ) : (
              <FileContent>{fileContent}</FileContent>
            )}
          </ModalContent>
        </Modal>
      )}
    </FileManagerContainer>
  );
};

export default FileManager; 