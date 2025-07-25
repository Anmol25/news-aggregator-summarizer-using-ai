import { useState, useRef, useEffect, useCallback } from 'react';
import News from '../News/News';
import PropTypes from 'prop-types';
import { useAxios } from '../../services/AxiosConfig';
import { debounce } from 'lodash';

function NewsLoader(props){
    const axiosInstance = useAxios();
    const {url, parameters, requestBody, setHasArticles} = props;
    const [items, setItems] = useState([]);
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);
    const loadingRef = useRef(false);

    const loadItems = useCallback(async (currentPage) => {
        if (loadingRef.current || !hasMore) return;
        loadingRef.current = true;

        try {
            let response;
            if (requestBody) {
                response = await axiosInstance.post(url, {...requestBody}, {
                    params: {
                        page: currentPage,
                        ...parameters
                    }
                });
            } else {
                response = await axiosInstance.get(url, {
                    params: {
                        page: currentPage,
                        ...parameters
                    }
                });
            }
            const newData = response.data || [];
            if (setHasArticles && newData.length > 0){
                setHasArticles(true);
            }
            const moreData = newData.length === 20;
            setItems(prev => currentPage === 1 ? newData : [...prev, ...newData]);
            setHasMore(moreData);
            setPage(currentPage + 1);
        } catch (error) {
            console.error('Error loading feed:', error);
            setHasMore(false);
        } finally {
            loadingRef.current = false;
        }
    }, [hasMore, axiosInstance]);

    useEffect(() => {
        setItems([]);
        setPage(1);
        setHasMore(true);
        loadingRef.current = false;
        loadItems(1);
    }, []);

    const handleScroll = useCallback(debounce(() => {
        if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 100) {
            loadItems(page);
        }
    }, 200), [loadItems, page]); // Adjust the delay (200ms) as needed

    useEffect(() => {
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, [handleScroll]);

    return(
        <div className="grid grid-cols-[repeat(auto-fill,minmax(300px,1fr))] gap-6">
    {items.map((item) => (
        <div key={item.id} className="aspect-square">
            <News {...item} />
        </div>
    ))}
    {hasMore ? (
        <div className="flex items-center justify-center h-16 col-span-full">
            <div className="w-6 h-6 border-4 border-gray-200 border-t-black rounded-full animate-spin"></div>
        </div>
    ) : items.length ? "" : (
        <div className="col-span-full flex items-center justify-center h-24">
            <p className="text-gray-500 text-lg">No Articles found</p>
        </div>
    )}
</div>
    )
}

NewsLoader.propTypes = {
    url: PropTypes.string.isRequired,
    parameters: PropTypes.object,
    requestBody: PropTypes.object,
    setHasArticles: PropTypes.func
};

export default NewsLoader;