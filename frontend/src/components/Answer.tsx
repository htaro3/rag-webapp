import React from 'react';
import styled from 'styled-components';

interface AnswerProps {
  answer: string;
  loading: boolean;
}

const AnswerContainer = styled.div`
  margin-top: 1rem;
  padding: 1.5rem;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  min-height: 200px;
  position: relative;
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
`;

const AnswerText = styled.div`
  white-space: pre-wrap;
  line-height: 1.6;
`;

const Answer: React.FC<AnswerProps> = ({ answer, loading }) => {
  if (loading) {
    return (
      <AnswerContainer>
        <LoadingContainer>
          <div className="loading-spinner" />
        </LoadingContainer>
      </AnswerContainer>
    );
  }

  if (!answer) {
    return (
      <AnswerContainer>
        <p>質問を入力すると、ここに回答が表示されます。</p>
      </AnswerContainer>
    );
  }

  return (
    <AnswerContainer>
      <h3>回答</h3>
      <AnswerText>{answer}</AnswerText>
    </AnswerContainer>
  );
};

export default Answer; 