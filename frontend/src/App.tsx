import React, { useState } from 'react';
import styled from 'styled-components';
import QuestionForm from './components/QuestionForm';
import DocumentUpload from './components/DocumentUpload';
import FileManager from './components/FileManager';
import Answer from './components/Answer';

const AppContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Roboto', sans-serif;
`;

const Header = styled.header`
  text-align: center;
  margin-bottom: 2rem;
`;

const Tabs = styled.div`
  display: flex;
  margin-bottom: 2rem;
  border-bottom: 1px solid #ddd;
`;

const Tab = styled.button<{ active: boolean }>`
  padding: 0.5rem 1rem;
  border: none;
  background: none;
  font-size: 1rem;
  cursor: pointer;
  border-bottom: 2px solid ${props => props.active ? '#2196f3' : 'transparent'};
  color: ${props => props.active ? '#2196f3' : '#333'};
  
  &:hover {
    background-color: #f5f5f5;
  }
`;

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'question' | 'upload' | 'manage'>('question');
  const [answer, setAnswer] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  return (
    <AppContainer>
      <Header>
        <h1>RAG Web Application</h1>
        <p>検索拡張生成（RAG）を用いた質問応答システム</p>
      </Header>
      
      <Tabs>
        <Tab 
          active={activeTab === 'question'} 
          onClick={() => setActiveTab('question')}
        >
          質問する
        </Tab>
        <Tab 
          active={activeTab === 'upload'} 
          onClick={() => setActiveTab('upload')}
        >
          文書をアップロード
        </Tab>
        <Tab 
          active={activeTab === 'manage'} 
          onClick={() => setActiveTab('manage')}
        >
          文書を管理
        </Tab>
      </Tabs>

      {activeTab === 'question' && (
        <>
          <QuestionForm 
            onAnswerReceived={setAnswer} 
            setLoading={setLoading} 
          />
          <Answer answer={answer} loading={loading} />
        </>
      )}
      
      {activeTab === 'upload' && (
        <DocumentUpload />
      )}
      
      {activeTab === 'manage' && (
        <FileManager />
      )}
    </AppContainer>
  );
};

export default App; 