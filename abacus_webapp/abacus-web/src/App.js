import {MyHome} from './pages/home';
import './app.css'
import {Navbar} from './navbar/navbar'
import { BrowserRouter as Router } from 'react-router-dom';

function App() {
  return (
    <div className='App'>
      <Router>
        <Navbar/>
      </Router>
      <MyHome/>
    </div>
  );
}

export default App;
