import './News.css';
import { useState, useEffect } from 'react';
import handleFallbackImage from '../../services/HandleFallbackImg';
import { useAxios } from '../../services/AxiosConfig';
import heart from '../../assets/Icons/heart.svg';
import bookmarked from '../../assets/Icons/bookmarked.svg';
import { NavLink } from 'react-router-dom';

function News(props) {
  const { image, source, title, link, published_date, id } = props;
  const axiosInstance = useAxios();
  const [summary, setSummary] = useState(null);
  const [displayText, setDisplayText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // State of Like and Bookmark Button
  const [isLiked, setIsLiked] = useState(props.liked);
  const [isBookmarked, setIsBookmarked] = useState(props.bookmarked);
  
  const fallbackImage = handleFallbackImage(source);

  const formatDate = (time) => {
    const date = new Date(time);

    const formattedDate = date.toLocaleString("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
    });

    const formattedTime = date.toLocaleString("en-IN", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
      timeZone: "Asia/Kolkata"
    }).replace(",", "");

    return [formattedDate, `${formattedTime} IST`];
  };

  useEffect(() => {
    if (!summary) return;

    setIsTyping(true);
    let index = 0;
    const typingSpeed = 5; // milliseconds
    
    const typingInterval = setInterval(() => {
      if (index < summary.length) {
        setDisplayText((prev) => prev + summary.charAt(index));
        index++;
      } else {
        clearInterval(typingInterval);
        setIsTyping(false);
      }
    }, typingSpeed);

    return () => clearInterval(typingInterval);
  }, [summary]);

  const handleSummarize = () => {
    setIsLoading(true);
    setDisplayText('');
    
    axiosInstance.get('/summarize', {
      params: { id }
    })
      .then((response) => {
        setSummary(response.data.data);
      })
      .catch((error) => {
        console.error('Error fetching summary:', error);
      })
      .finally(() => {
        setIsLoading(false);
      });
  };

  const [dateFormatted, timeFormatted] = formatDate(published_date);

  const handleLike = async () => {
    const response = await axiosInstance.post('/like', {
      article_id: props.id
    });

    if (response.status === 200) {
      setIsLiked(!isLiked);
    }
  };
  
  const handleBookmark = async () => {
    const response = await axiosInstance.post('/bookmark', {
      article_id: props.id
    });

    if (response.status === 200) {
      setIsBookmarked(!isBookmarked);
    }
  };

  return (
    <div className="NewsBlock">
      {!summary && <img className="NewsImage" src={image || fallbackImage} alt={title} onError={(e) => e.target.src = fallbackImage}/>}
      
      <div className="NewsContent">
        <a className="NewsTitle" href={link} target="_blank" rel="noopener noreferrer">
          {title}
        </a>
        
        <div className="NewsInfo">
          <p className="NewsMetaData">{dateFormatted}</p>
          <p className="NewsMetaData">{timeFormatted}</p>
        </div>
        
        <div className="NewsInfo">
          <div className="source-follow">
            <NavLink className="source" to={`/source/${source.toLowerCase().replace(/\s+/g, '-')}`}>
              {source}
            </NavLink>
          </div>
          
          <div>
            <img className={`news-buttons ${isLiked ? "black-filter" : ""}`} src={heart} alt="Like" onClick={handleLike}/>
            <img className={`news-buttons ${isBookmarked ? "black-filter" : ""}`} src={bookmarked} alt="Bookmark" onClick={handleBookmark}/>
          </div>
        </div>
        
        {summary && (
          <div className="NewsSummaryContainer">
            <p className={`NewsSummary ${isTyping ? 'typing' : ''}`}>
              {displayText}
            </p>
          </div>
        )}
      </div>
      
      {!summary && (
        <button 
          className={`SummarizeButton ${isLoading ? 'loading' : ''}`}
          onClick={handleSummarize}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              Summarizing
              <span className="spinner" />
            </>
          ) : (
            'Summarize'
          )}
        </button>
      )}
    </div>
  );
}

export default News;