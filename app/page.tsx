"use client";

import React from "react";
import menuData from "../public/menus.json";
import RestaurantCard from "./RestaurantCard";

const daysInSwedish = [
  "söndagens",
  "måndagens",
  "tisdagens",
  "onsdagens",
  "torsdagens",
  "fredagens",
  "lördagens",
];

export default function Home() {
  const sortedMenuData = menuData.restaurants.sort((a, b) =>
    a.name.localeCompare(b.name)
  );

  const today = new Date().getDay();
  const todayInSwedish = daysInSwedish[today];

  const todayTextLength = todayInSwedish.length;

  return (
    <div className="">
      <section className="relative bg-gradient-to-b from-zinc-900 to-zinc-800 text-center py-12 px-4 shadow-lg">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-100 leading-tight max-w-3xl mx-auto">
          Upptäck{" "}
          <span
            className={`text-yellow-400 inline-block min-w-[${todayTextLength}ch]`}
          >
            {todayInSwedish}
          </span>{" "}
          bästa lunchalternativ i Alvik
        </h1>
        <p className="text-gray-300 mt-4 max-w-xl mx-auto text-lg">
          En samlad översikt över dagens menyer från restauranger nära dig.
        </p>
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
