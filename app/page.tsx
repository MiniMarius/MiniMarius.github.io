
'use client'
import React, { useState, useEffect } from "react";
import menuData from "../public/menus.json";
import logo from "../public/alvikslunchen.png";
import RestaurantCard from "./RestaurantCard";

const daysInSwedish = ["söndagens", "måndagens", "tisdagens", "onsdagens", "torsdagens", "fredagens", "lördagens"];

export default function Home() {
  const sortedMenuData = menuData.restaurants.sort((a, b) =>
    a.name.localeCompare(b.name)
  );

  const [text, setText] = useState("dagens");
  const today = new Date().getDay();
  const todayInSwedish = daysInSwedish[today];

  useEffect(() => {
    // Change text initially after the first animation
    const initialTimeout = setTimeout(() => {
      setText(todayInSwedish);
    }, 3500);

    const interval = setInterval(() => {
      setTimeout(() => {
        setText((prevText) => (prevText === "dagens" ? todayInSwedish : "dagens"));
      }, 3500);
    }, 5000);
  
    return () => {
      clearTimeout(initialTimeout);
      clearInterval(interval);
    };
  }, [todayInSwedish]);

  // Calculate minimum width based on today's Swedish name
  const todayTextLength = todayInSwedish.length;

  return (
    <div className="p-4">
      <section className="hero bg-zinc-800 text-center py-16">
        <h1 className="text-4xl font-bold text-gray-200">
          Upptäck <span className={`text-yellow-400 rotate-text inline-block min-w-[${todayTextLength}ch]`}>{text}</span> bästa lunchalternativ i Alvik!
        </h1>
      </section>
      <div className="flex justify-center mt-8">
        <div className="w-full max-w-screen-2xl">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {sortedMenuData.map((restaurant) => (
              <div key={restaurant.name} className="overflow-hidden">
                <RestaurantCard restaurant={restaurant} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
