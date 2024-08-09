"use client";

import { useState, useEffect, useRef } from "react";
import axios from 'axios';
import { Chart, ArcElement, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';
import Image from 'next/image';
import TweetMockup from '../components/TweetMockup'; // Importe o componente de tweet
import WhiteLogo from '../assets/WhiteLogo.png';

Chart.register(ArcElement, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

export default function Home() {
  const [chartData, setChartData] = useState<number[]>([0, 0]);
  const [gaugeValue, setGaugeValue] = useState<number>(0);
  const gaugeChartRef = useRef<any>(null);
  const [gradient, setGradient] = useState<any>();

  const [negativeTweets, setNegativeTweets] = useState<string[]>([]);
  const [positiveTweets, setPositiveTweets] = useState<string[]>([]);

  useEffect(() => {
    fetchGraphData(30);
    fetchLastTweets();
  }, []);

  const fetchGraphData = async (days: number) => {
    try {
      const response = await axios.get(`http://localhost:5000/infos/graph-infos/${days}`);
      const data = response.data;
      console.log('Graph data:', data);
      const sentimentCounts = [data.negative, data.positive];
      setChartData(sentimentCounts);

      const totalSentiments = sentimentCounts.reduce((a, b) => a + b, 0);
      const gaugeValue = totalSentiments > 0 ? (sentimentCounts[0] / totalSentiments) * 100 : 0;
      setGaugeValue(gaugeValue);
    } catch (error) {
      console.error('Error fetching graph data:', error);
    }
  };

  const fetchLastTweets = async () => {
    try {
      const response = await axios.get('http://localhost:5000/infos/last_tweets');
      const tweets = response.data.last_tweets;
      console.log('Last tweets:', tweets);
      // const negative = tweets.filter((tweet: any) => tweet[2] === 0).map((tweet: any) => tweet[1]);
      // const positive = tweets.filter((tweet: any) => tweet[2] === 1).map((tweet: any) => tweet[1]);

      // console.log('Negative tweets:', negative);
      // console.log('Positive tweets:', positive);

      // setNegativeTweets(negative);
      // setPositiveTweets(positive);
    } catch (error) {
      console.error('Error fetching last tweets:', error);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    console.log('File uploaded:', file);
    if (file) {
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await axios.post('http://localhost:5000/clean_data/csv', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        console.log('File processed successfully:', response.data);
        fetchGraphData(7);  // Re-fetch graph data after file upload
        fetchLastTweets();  // Re-fetch tweets after file upload
      } catch (error) {
        console.error('Error uploading file:', error.response.data);
      }
    }
  };

  useEffect(() => {
    if (gaugeChartRef.current) {
      const chart = gaugeChartRef.current;
      const ctx = chart.ctx;
      const gradient = ctx.createLinearGradient(0, 0, ctx.canvas.width, 0);
      gradient.addColorStop(0, '#FF4560'); // Vermelho
      gradient.addColorStop(0.5, '#FFDD59'); // Amarelo
      gradient.addColorStop(1, '#00E396'); // Verde
      setGradient(gradient);
    }
  }, [gaugeValue]);

  const gaugeOptions = {
    circumference: 180,
    rotation: -90,
    cutout: '70%',
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        enabled: false
      }
    }
  };

  const gaugeData = {
    labels: ['Negativo', 'Restante'],
    datasets: [
      {
        data: [gaugeValue, 100 - gaugeValue],
        backgroundColor: [gradient, '#E0E0E0'],
        borderWidth: 0,
      },
    ],
  };

  const barData = {
    labels: ['Negativo', 'Positivo'],
    datasets: [
      {
        label: 'Sentimentos',
        data: chartData,
        backgroundColor: ['#FF4560', '#00E396'],
      },
    ],
  };

  const barOptions = {
    indexAxis: 'y' as const,
    scales: {
      x: {
        beginAtZero: true,
        ticks: {
          color: '#D3D3D3',  // Cor dos textos do eixo x
        },
      },
      y: {
        ticks: {
          color: '#D3D3D3',  // Cor dos textos do eixo y
        },
      },
    },
    elements: {
      bar: {
        borderWidth: 1,
        borderRadius: 10,  // Bordas arredondadas
      },
    },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        enabled: true,
        bodyColor: '#D3D3D3',  // Cor do texto do tooltip
        titleColor: '#D3D3D3',  // Cor do título do tooltip
      }
    },
    maintainAspectRatio: false,  // Permite ajustar a altura
  };

  return (
    <div className="flex min-h-screen flex-col items-start justify-start pt-0">
      <nav className="flex flex-row w-full justify-between items-center bg-zinc-950 shadow-md px-7 py-3">
        <Image src={WhiteLogo} height={20} alt="Logo" />
        <div className="flex flex-col items-center space-y-4">
          <label
            htmlFor="file-upload"
            className="cursor-pointer bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            Upload CSV
          </label>
          <input
            id="file-upload"
            type="file"
            accept=".csv"
            className="hidden"
            onChange={handleFileUpload}
          />
        </div>
      </nav>
      <main className="flex h-full w-full flex-col items-center justify-start p-24 pt-0 space-y-8">
        <div className="w-full flex flex-row mt-16 justify-between items-center">
          <TweetMockup text={negativeTweets[0] || "No negative tweets available"} dotColor="#fc0303"/>
          <TweetMockup text={positiveTweets[0] || "No positive tweets available"} dotColor="#3dfc03"/>
        </div>
        <div className="flex w-full my-24 flex-row gap-10">
          {gaugeValue >= 0 && (
            <div id="chart" className="p-4 bg-zinc-800 rounded-lg shadow-lg">
              <Doughnut ref={gaugeChartRef} data={gaugeData} options={gaugeOptions} />
              <div className="text-center mt-4">
                <h2 className="text-2xl font-bold text-white">{gaugeValue.toFixed(2)}%</h2>
              </div>
            </div>
          )}
          {chartData && chartData.length > 0 && (
            <div id="bar-chart" className="max-w-full w-[80%] h-96 p-4 bg-zinc-800 rounded-lg shadow-lg"> 
              <Bar data={barData} options={barOptions} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
