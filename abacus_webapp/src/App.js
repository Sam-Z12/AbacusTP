import {MyHome} from './pages/home';
import { PaperTradePage } from './pages/paper_trade';
import { AlgorithmsPage } from './pages/algorithms';
import { LoginPage } from './pages/login';
import './app.css'
import {Navbar} from './navbar/navbar'
import { BrowserRouter as Router, Route, Routes} from 'react-router-dom';


function App() {
  return (
    <div className='App'>
      <Router>
        <Navbar/>
        <Routes>
          <Route path='/' element={<MyHome/>}/>
          <Route path='/paper_trade' element={<PaperTradePage/>}/>
          <Route path='/algorithms' element={<AlgorithmsPage/>}/>
          <Route path='/login' element={<LoginPage/>}/>
        </Routes>
      </Router>

    </div>
  );
}

export default App;
