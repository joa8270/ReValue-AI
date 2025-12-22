
import React, { useState, useEffect } from 'react';
import { X, Mail, Lock, User, LogIn, UserPlus } from 'lucide-react';
import { User as UserType } from '../types';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLogin: (user: UserType) => void;
}

const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');

  // 當切換模式時清除錯誤訊息
  useEffect(() => {
    setError('');
  }, [isLogin]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // 調試訊息：開始驗證過程
    console.log(`[Auth] Attempting ${isLogin ? 'Login' : 'Registration'} for: ${email}`);

    try {
      // 1. 從 localStorage 獲取所有用戶
      const rawUsers = localStorage.getItem('vc_users');
      let users = [];
      if (rawUsers) {
        users = JSON.parse(rawUsers);
      }
      
      console.log(`[Auth] Current DB count: ${users.length}`);

      if (isLogin) {
        // 登入邏輯
        const user = users.find((u: any) => u.email.toLowerCase() === email.toLowerCase());
        
        if (!user) {
          setError('找不到此帳號，請確認 Email 是否正確 / Email not found');
          return;
        }

        if (user.password !== password) {
          setError('密碼錯誤 / Incorrect password');
          return;
        }

        console.log(`[Auth] Login Successful:`, user.name);
        onLogin({ id: user.id, email: user.email, name: user.name });
        onClose();
      } else {
        // 註冊邏輯
        const existingUser = users.find((u: any) => u.email.toLowerCase() === email.toLowerCase());
        if (existingUser) {
          setError('此電子郵件已註冊過 / Email already exists. Please login instead.');
          return;
        }

        const newUser = { 
          id: Date.now().toString(), 
          email: email.toLowerCase(), 
          password, 
          name: name || 'User' 
        };

        // 2. 將新用戶加入陣列並寫回 localStorage
        users.push(newUser);
        localStorage.setItem('vc_users', JSON.stringify(users));
        
        // 驗證是否成功寫入
        const verifyWrite = localStorage.getItem('vc_users');
        console.log(`[Auth] Register Successful. New DB size: ${JSON.parse(verifyWrite || '[]').length}`);

        onLogin({ id: newUser.id, email: newUser.email, name: newUser.name });
        onClose();
      }
    } catch (err) {
      console.error("[Auth] Fatal Error:", err);
      setError('發生系統錯誤，請重試 / System error. Please try again.');
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 z-[70] flex items-center justify-center p-4 backdrop-blur-md">
      <div className="bg-slate-900 rounded-[2.5rem] w-full max-w-md overflow-hidden shadow-2xl border border-slate-800 animate-in fade-in zoom-in-95 duration-300">
        <div className="p-10 relative">
          <button onClick={onClose} className="absolute top-8 right-8 text-slate-500 hover:text-slate-100 transition-colors">
            <X className="w-6 h-6" />
          </button>
          
          <div className="text-center mb-10">
            <h3 className="text-3xl font-black text-white mb-2 tracking-tight">
              {isLogin ? '歡迎回來 / Welcome' : '建立帳戶 / Join Us'}
            </h3>
            <p className="text-sm text-slate-400 font-medium leading-relaxed">
              Login to save your valuation history and exclusive advice.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {!isLogin && (
              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-500 ml-1 uppercase tracking-widest">Name / 名稱</label>
                <div className="relative">
                  <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    required
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl pl-11 pr-4 py-3.5 text-slate-100 focus:ring-2 focus:ring-indigo-500/50 outline-none transition-all placeholder:text-slate-600"
                    placeholder="您的稱呼"
                  />
                </div>
              </div>
            )}

            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-500 ml-1 uppercase tracking-widest">Email / 電子郵件</label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  required
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl pl-11 pr-4 py-3.5 text-slate-100 focus:ring-2 focus:ring-indigo-500/50 outline-none transition-all placeholder:text-slate-600 font-mono"
                  placeholder="name@example.com"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-500 ml-1 uppercase tracking-widest">Password / 密碼</label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  required
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl pl-11 pr-4 py-3.5 text-slate-100 focus:ring-2 focus:ring-indigo-500/50 outline-none transition-all placeholder:text-slate-600"
                  placeholder="••••••••"
                />
              </div>
            </div>

            {error && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-3">
                <p className="text-xs text-red-400 text-center font-bold">{error}</p>
              </div>
            )}

            <button
              type="submit"
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-black py-4 rounded-2xl shadow-xl shadow-indigo-500/20 flex items-center justify-center gap-2 transition-all active:scale-[0.98] uppercase tracking-wider"
            >
              {isLogin ? <LogIn className="w-5 h-5" /> : <UserPlus className="w-5 h-5" />}
              {isLogin ? '立即登入 / Login' : '註冊帳戶 / Register'}
            </button>
          </form>

          <div className="mt-10 pt-8 border-t border-slate-800 text-center">
            <button
              type="button"
              onClick={() => setIsLogin(!isLogin)}
              className="text-sm font-bold text-indigo-400 hover:text-indigo-300 transition-colors uppercase tracking-tight"
            >
              {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Login'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthModal;
