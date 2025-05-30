import axios from 'axios';

/**
 * 質問を送信し、回答を取得する
 */
export const askQuestion = async (question: string): Promise<string> => {
  try {
    const response = await axios.post('/api/ask', { question });
    return response.data.answer;
  } catch (error) {
    console.error('Error in askQuestion:', error);
    throw new Error('質問の処理中にエラーが発生しました');
  }
}; 