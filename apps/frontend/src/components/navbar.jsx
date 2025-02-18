import logo from '../assets/logo.png';
import '../styles/navbar.css';

function Navbar(){
    return (
        <div className="navbar">
            <img className='logo' src={logo} alt="News Digest"/>
            <form className='Searchbar'>
                <input type="text" placeholder="Search" name="search"/>
                <button className='searchbutton' type="submit">Search</button>
            </form>
            <p className='profile'>Profile</p>
        </div>
    )
}

export default Navbar;