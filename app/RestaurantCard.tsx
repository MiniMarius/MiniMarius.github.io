
'use client'
import React, { useState } from "react";
import { ChevronDownIcon } from "@radix-ui/react-icons";

// Import images
import alcamImage from "../public/alcam.jpg";
import bastardImage from "../public/bastard.jpeg";
import garrosImage from "../public/garros.jpg";
import melandersImage from "../public/Melanders.jpg";
import pokeburgerImage from "../public/poké-burger.jpg";
import sjopaviljongenImage from "../public/sjopaviljongen.jpg";

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

// Map restaurant names to imported images
const restaurantImages: { [key: string]: string } = {
  "Al Caminetto": alcamImage.src,
  "Bastard Burgers": bastardImage.src,
  "Bistro Garros": garrosImage.src,
  "Melanders": melandersImage.src,
  "Poké Burger": pokeburgerImage.src,
  "Sjöpaviljongen": sjopaviljongenImage.src,
};

const RestaurantCard: React.FC<RestaurantCardProps> = ({ restaurant }) => {
  // Get the image source based on the restaurant name
  const imageSrc = restaurantImages[restaurant.name];

  // State to manage the toggle
  const [isExpanded, setIsExpanded] = useState(false);

  const handleToggle = () => {
    setIsExpanded((prev) => !prev);
  };

  return (
    <div className="w-full max-w-md rounded-lg shadow-md overflow-hidden bg-zinc-800">
      <div className="cursor-pointer block" onClick={handleToggle}>
        <img
          src={imageSrc}
          alt={`${restaurant.name} image`}
          className="w-full h-48 object-cover"
        />
        <div className="p-4">
          <h2 className="text-lg font-bold text-yellow-400">{restaurant.name}</h2>
          <div className="mt-2 text-yellow-300 flex items-center">
            <span>{isExpanded ? "Dölj meny" : "Visa meny"}</span>
            <ChevronDownIcon
              className={`ml-1 transition-transform duration-300 ${
                isExpanded ? "rotate-180" : ""
              }`}
            />
          </div>
        </div>
      </div>
      <div
        className={`p-4 transition-max-height duration-300 ${
          isExpanded ? "max-h-full" : "max-h-0 overflow-hidden"
        }`}
      >
        {restaurant.menu.map((section, sectionIndex) => (
          <div key={sectionIndex} className="mt-4 border-t border-zinc-500 pt-4">
            <h4 className="text-lg font-semibold mb-2 text-yellow-400">{section.title}</h4>
            <ul className="list-disc list-inside">
              {section.dishes.map((dish, dishIndex) => (
                <li className="text-yellow-300 mb-2" key={dishIndex}>
                  {dish.name}{" "}
                  {dish.price && (
                    <span className="text-yellow-200">- {dish.price.toFixed(2)} kr</span>
                  )}
                  {dish.description && (
                    <p className="text-yellow-200">{dish.description}</p>
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
