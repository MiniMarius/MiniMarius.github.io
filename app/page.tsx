
'use client';

import React from "react";
import menuData from "../public/menus.json";
import RestaurantCard from "./RestaurantCard";

const daysInSwedish = [
  "söndagens", "måndagens", "tisdagens", "onsdagens", 
  "torsdagens", "fredagens", "lördagens"
];

export default function Home() {
  const sortedMenuData = menuData.restaurants.sort((a, b) =>
    a.name.localeCompare(b.name)
  );

  const today = new Date().getDay();
  const todayInSwedish = daysInSwedish[today];

  const todayTextLength = todayInSwedish.length;

  return (
    <div className="p-4">
      <section className="hero bg-zinc-800 text-center py-16">
        <h1 className="text-4xl font-bold text-gray-200">
          Upptäck <span className={`text-yellow-400 inline-block min-w-[${todayTextLength}ch]`}>{todayInSwedish}</span> bästa lunchalternativ i Alvik!
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
