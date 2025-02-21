import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LoginForm from '../components/AuthComponent/LoginForm';

const Login = () => {
  const { accessToken } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (accessToken) {
      navigate('/');
    } else {
      navigate('/login');
    }
  }, [accessToken, navigate]);

  return (
    <LoginForm />
  );
};

export default Login;