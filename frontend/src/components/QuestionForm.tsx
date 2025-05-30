import React, { useState } from 'react';
import styled from 'styled-components';
import { askQuestion } from '../api/questionApi';

interface QuestionFormProps {
  onAnswerReceived: (answer: string) => void;
  setLoading: (loading: boolean) => void;
}

const Form = styled.form`
  display: flex;
  flex-direction: column;
  margin-bottom: 2rem;
`;

const Textarea = styled.textarea`
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  min-height: 100px;
  margin-bottom: 1rem;
  resize: vertical;
`;

const ButtonContainer = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
`;

const Button = styled.button`
  padding: 0.75rem 1.5rem;
  background-color: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  
  &:hover {
    background-color: #1976d2;
  }
  
  &:disabled {
    background-color: #bdbdbd;
    cursor: not-allowed;
  }
`;

const ClearButton = styled(Button)`
  background-color: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
  
  &:hover {
    background-color: #e0e0e0;
  }
`;

const QuestionForm: React.FC<QuestionFormProps> = ({ onAnswerReceived, setLoading }) => {
  const [question, setQuestion] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!question.trim()) return;
    
    setIsSubmitting(true);
    setLoading(true);
    
    try {
      const answer = await askQuestion(question);
      onAnswerReceived(answer);
    } catch (error) {
      console.error('Error asking question:', error);
      onAnswerReceived('質問の処理中にエラーが発生しました。もう一度お試しください。');
    } finally {
      setIsSubmitting(false);
      setLoading(false);
    }
  };

  const handleClear = () => {
    setQuestion('');
    // 回答もクリアする
    onAnswerReceived('');
  };

  return (
    <Form onSubmit={handleSubmit}>
      <h2>質問する</h2>
      <p>アップロードした文書に関連する質問を入力してください：</p>
      <Textarea 
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="例：このドキュメントの要点は何ですか？"
        disabled={isSubmitting}
      />
      <ButtonContainer>
        <ClearButton 
          type="button" 
          onClick={handleClear} 
          disabled={isSubmitting || !question.trim()}
        >
          クリア
        </ClearButton>
        <Button type="submit" disabled={isSubmitting || !question.trim()}>
          {isSubmitting ? '処理中...' : '質問する'}
        </Button>
      </ButtonContainer>
    </Form>
  );
};

export default QuestionForm; 