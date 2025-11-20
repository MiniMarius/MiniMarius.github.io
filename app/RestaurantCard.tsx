"use client";

import React, { useState, useRef, useEffect } from "react";
import { ChevronDownIcon } from "@radix-ui/react-icons";

// Import images
import alcamImage from "../public/alcam.jpg";
import bastardImage from "../public/bastard.jpeg";
import garrosImage from "../public/garros.jpg";
import melandersImage from "../public/Melanders.jpg";
import pokeburgerImage from "../public/poké-burger.jpg";
import sjopaviljongenImage from "../public/sjopaviljongen.jpg";
import caffenero from "../public/caffenero.jpg";
import joejuice from "../public/joejuice.png";
import megiart from "../public/meegisartsushi.png";
import brioche from "../public/brioche.jpg";
import vedugnen from "../public/vedugnen.jpg";

interface RestaurantCardProps {
  restaurant: {
    name: string;
    menu: Array<{
      title: string;
      dishes: Array<{
        name: string;
        price?: number;
        description?: string;
      }>;
    }>;
  };
}

const restaurantImages: { [key: string]: string } = {
  "Al Caminetto": alcamImage.src,
  "Bastard Burgers": bastardImage.src,
  "Bistro Garros": garrosImage.src,
  Melanders: melandersImage.src,
  "Poké Burger": pokeburgerImage.src,
  Sjöpaviljongen: sjopaviljongenImage.src,
  "Caffé Nero": caffenero.src,
  "Joe & the Juice": joejuice.src,
  "Meegi Art Sushi": megiart.src,
  Brioche: brioche.src,
  Vedugnen: vedugnen.src,
};

const RestaurantCard: React.FC<RestaurantCardProps> = ({ restaurant }) => {
  const imageSrc = restaurantImages[restaurant.name];
  const [isExpanded, setIsExpanded] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);

  const handleToggle = () => {
    if (restaurant.menu.length > 0) {
      setIsExpanded((prev) => !prev);
    }
  };

  useEffect(() => {
    if (contentRef.current) {
      contentRef.current.style.maxHeight = isExpanded
        ? `${contentRef.current.scrollHeight}px`
        : "0px";
    }
  }, [isExpanded]);
  return (
    <div
      className="
      w-full max-w-md rounded-2xl 
      bg-zinc-800/40 backdrop-blur-xl 
      border border-zinc-700/40 
      shadow-xl shadow-black/30 
      transition-all duration-300
      hover:shadow-2xl hover:shadow-black/50 
      hover:-translate-y-1
      overflow-hidden
    "
    >
      <div className="cursor-pointer relative" onClick={handleToggle}>
        {/* Glass highlight overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent pointer-events-none" />

        <img
          src={imageSrc}
          alt={`${restaurant.name} image`}
          className="w-full h-48 object-cover"
        />

        <div className="p-5">
          <h2 className="text-2xl font-bold text-yellow-300 drop-shadow-md">
            {restaurant.name}
          </h2>

          <div className="mt-2 text-yellow-200/90 flex items-center">
            <span>
              {restaurant.menu.length === 0
                ? "Menyn är inte tillgänglig"
                : isExpanded
                ? "Dölj meny"
                : "Visa meny"}
            </span>
            <ChevronDownIcon
              className={`ml-1 transition-transform duration-300 ${
                isExpanded ? "rotate-180" : ""
              }`}
            />
          </div>
        </div>
      </div>

      {/* Expanding content section */}
      <div
        ref={contentRef}
        className={`
    px-5 pb-4 pt-0
    transition-max-height duration-300 
    overflow-hidden
    bg-zinc-900/40 backdrop-blur-xl
    ${isExpanded ? "border-t border-zinc-700/40" : ""}
  `}
        style={{
          maxHeight: isExpanded
            ? `${contentRef.current?.scrollHeight}px`
            : "0px",
        }}
      >
        {restaurant.menu.map((section, sectionIndex) => (
          <div key={sectionIndex} className="mt-4 pt-4">
            <h4 className="text-lg font-semibold mb-2 text-yellow-300">
              {section.title}
            </h4>

            <ul className="space-y-2">
              {section.dishes.map((dish, dishIndex) => (
                <li className="text-yellow-200/90" key={dishIndex}>
                  <span className="font-medium">{dish.name}</span>{" "}
                  {dish.price !== undefined && dish.price > 0 && (
                    <span className="text-yellow-300/70">
                      – {dish.price.toFixed(2)} kr
                    </span>
                  )}
                  {dish.description && (
                    <p className="text-yellow-300/60 text-sm mt-1">
                      {dish.description}
                    </p>
                  )}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RestaurantCard;
