'use client'

// components/TweetMockup.tsx
interface TweetMockupProps {
  text: string;
  dotColor: string;
}

const TweetMockup: React.FC<TweetMockupProps> = ({ text, dotColor }) => {
  return (
    <div className="bg-black text-white p-4 rounded-lg w-[32%] min-h-full shadow-lg">
      <div className="flex items-center mb-4">
        <img
          src="https://via.placeholder.com/48"
          alt="Profile Picture"
          className="w-12 h-12 rounded-full mr-3"
        />
        <div className="w-full">
          <div className="flex w-full justify-between">
            <div className="flex flex-row items-center">
              <span className="font-bold text-white">Usuário Anônimo</span>
              <img
                src="https://upload.wikimedia.org/wikipedia/commons/e/e4/Twitter_Verified_Badge.svg"
                alt="Verified Badge"
                className="ml-2 w-5 h-5"
              />
            </div>
            <div className={`w-4 h-4 rounded-full self-end`} style={{backgroundColor: dotColor}}/>
          </div>
          <span className="text-gray-500">@twitterhandle</span>
        </div>
      </div>
      <div className="text-gray-200 mb-4">
        {text}
      </div>
      <div className="flex justify-between text-gray-500 text-sm">
        <div className="flex items-center">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" className="mr-1">
            <path d="M12 23c6.074 0 11-4.926 11-11S18.074 1 12 1 1 5.926 1 12s4.926 11 11 11zM9.216 17.27c-.548 0-.993-.445-.993-.993v-3.98H5.756c-.548 0-.993-.445-.993-.993s.445-.993.993-.993h2.467V6.746c0-.548.445-.993.993-.993s.993.445.993.993v3.98h2.467c.548 0 .993.445.993.993s-.445.993-.993.993h-2.467v3.98c0 .548-.445.993-.993.993zm9.384-5.27h-3.384V9.384h3.384v3.384z"></path>
          </svg>
          85 Retweets
        </div>
        <div className="flex items-center">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" className="mr-1">
            <path d="M12 23c6.074 0 11-4.926 11-11S18.074 1 12 1 1 5.926 1 12s4.926 11 11 11zm2.25-16.5a2.25 2.25 0 110 4.5 2.25 2.25 0 010-4.5zM8.25 6.75a2.25 2.25 0 110 4.5 2.25 2.25 0 010-4.5zM12 18a6 6 0 01-4.8-2.4c.048-.192.288-.24.48-.24h9.12c.192 0 .432.048.48.24A6 6 0 0112 18z"></path>
          </svg>
          35 Quote Tweets
        </div>
        <div className="flex items-center">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" className="mr-1">
            <path d="M12 23c6.074 0 11-4.926 11-11S18.074 1 12 1 1 5.926 1 12s4.926 11 11 11zm0-20c4.963 0 9 4.037 9 9s-4.037 9-9 9-9-4.037-9-9 4.037-9 9-9zM8.9 15.1c.126.057.24.105.336.18.678.527 1.422.82 2.264.82.84 0 1.585-.293 2.264-.82a2.255 2.255 0 00.336-.18c.17-.088.353.085.282.26-.197.464-.678.8-.993.8s-.796-.336-.993-.8c-.071-.175.112-.348.282-.26.096-.075.21-.123.336-.18.678-.527 1.422-.82 2.264-.82.84 0 1.585.293 2.264.82a2.255 2.255 0 00.336.18c.17.088.353-.085.282-.26-.197-.464-.678-.8-.993-.8s-.796.336-.993.8c-.071.175.112.348.282.26.096.075.21.123.336.18.678.527 1.422.82 2.264.82.84 0 1.585-.293 2.264-.82a2.255 2.255 0 00.336-.18c.17-.088.353.085.282.26-.197.464-.678.8-.993.8s-.796-.336-.993-.8c-.071-.175.112-.348.282-.26.096-.075.21-.123.336-.18z"></path>
          </svg>
          1,279 Likes
        </div>
      </div>
    </div>
  );
};

export default TweetMockup;
