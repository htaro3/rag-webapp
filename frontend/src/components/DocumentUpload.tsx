import React, { useState } from 'react';
import styled from 'styled-components';
import { uploadDocument } from '../api/documentApi';

const UploadContainer = styled.div`
  margin-bottom: 2rem;
`;

const UploadForm = styled.form`
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
`;

const FileInputLabel = styled.label`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  border: 2px dashed #2196f3;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 1rem;
  transition: all 0.2s;
  
  &:hover {
    background-color: rgba(33, 150, 243, 0.05);
  }
`;

const FileInput = styled.input`
  display: none;
`;

const UploadButton = styled.button`
  padding: 0.75rem 1.5rem;
  background-color: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  align-self: flex-end;
  
  &:hover {
    background-color: #1976d2;
  }
  
  &:disabled {
    background-color: #bdbdbd;
    cursor: not-allowed;
  }
`;

const Message = styled.div<{ isError?: boolean }>`
  padding: 1rem;
  margin-top: 1rem;
  border-radius: 4px;
  background-color: ${props => props.isError ? '#ffebee' : '#e8f5e9'};
  color: ${props => props.isError ? '#c62828' : '#2e7d32'};
  border-left: 4px solid ${props => props.isError ? '#c62828' : '#2e7d32'};
`;

const FileList = styled.ul`
  list-style-type: none;
  padding: 0;
  margin: 1rem 0;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
`;

const FileItem = styled.li`
  padding: 0.5rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e0e0e0;
  
  &:last-child {
    border-bottom: none;
  }
`;

const RemoveButton = styled.button`
  background: none;
  border: none;
  color: #f44336;
  cursor: pointer;
  font-size: 1rem;
  padding: 0.25rem;
  
  &:hover {
    color: #d32f2f;
  }
`;

const DocumentUpload: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState<{ text: string; isError: boolean } | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files;
    if (selectedFiles && selectedFiles.length > 0) {
      // FileListをFile[]に変換
      const newFiles = Array.from(selectedFiles);
      setFiles(prev => [...prev, ...newFiles]);
      setMessage(null);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };
  
  const handleDrop = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      // FileListをFile[]に変換
      const newFiles = Array.from(e.dataTransfer.files);
      setFiles(prev => [...prev, ...newFiles]);
      setMessage(null);
    }
  };

  const removeFile = (indexToRemove: number) => {
    setFiles(files.filter((_, index) => index !== indexToRemove));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (files.length === 0) return;
    
    setIsUploading(true);
    setMessage(null);
    
    try {
      // 複数ファイルを順番にアップロード
      let successCount = 0;
      let errorCount = 0;

      for (const file of files) {
        try {
          await uploadDocument(file);
          successCount++;
        } catch (error) {
          console.error(`Error uploading ${file.name}:`, error);
          errorCount++;
        }
      }

      if (errorCount === 0) {
        setMessage({
          text: `${successCount}件のファイルアップロードに成功しました。`,
          isError: false
        });
        setFiles([]);
      } else {
        setMessage({
          text: `${successCount}件のアップロードに成功、${errorCount}件に失敗しました。`,
          isError: true
        });
      }
    } catch (error) {
      console.error('Error uploading documents:', error);
      setMessage({
        text: 'ファイルのアップロード中にエラーが発生しました。もう一度お試しください。',
        isError: true
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <UploadContainer>
      <h2>文書をアップロード</h2>
      <p>テキスト (.txt) 形式の文書をアップロードすると、検索と質問応答に利用できます。</p>
      
      <UploadForm onSubmit={handleSubmit}>
        <FileInputLabel 
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <svg 
            width="48" 
            height="48" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="#2196f3" 
            strokeWidth="2" 
            strokeLinecap="round" 
            strokeLinejoin="round"
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
          <p>クリックまたはドラッグ＆ドロップで複数ファイルを選択</p>
          <FileInput 
            type="file" 
            accept=".txt" 
            onChange={handleFileChange} 
            disabled={isUploading}
            multiple
          />
        </FileInputLabel>
        
        {files.length > 0 && (
          <FileList>
            {files.map((file, index) => (
              <FileItem key={index}>
                <span>{file.name}</span>
                <RemoveButton 
                  type="button" 
                  onClick={() => removeFile(index)}
                  disabled={isUploading}
                >
                  ✕
                </RemoveButton>
              </FileItem>
            ))}
          </FileList>
        )}
        
        <UploadButton type="submit" disabled={files.length === 0 || isUploading}>
          {isUploading ? 'アップロード中...' : `アップロード (${files.length}件)`}
        </UploadButton>
      </UploadForm>
      
      {message && (
        <Message isError={message.isError}>
          {message.text}
        </Message>
      )}
    </UploadContainer>
  );
};

export default DocumentUpload; 