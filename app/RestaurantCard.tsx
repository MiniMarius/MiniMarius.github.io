
import React from "react";
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

  return (
    <div className="w-full rounded-lg shadow-md overflow-hidden bg-zinc-800">
      <img
        src={imageSrc}
        alt={`${restaurant.name} image`}
        className="w-full h-48 object-cover"
      />
      <div className="p-4">
        <h2 className="text-lg font-bold text-yellow-400">{restaurant.name}</h2>

        <input type="checkbox" id={`toggle-${restaurant.name}`} className="hidden peer" />
        <label htmlFor={`toggle-${restaurant.name}`} className="mt-2 text-yellow-300 flex items-center cursor-pointer">
          <span className="peer-checked:hidden">View Menu</span>
          <span className="hidden peer-checked:inline">Hide Menu</span>
          <ChevronDownIcon className="ml-1" />
        </label>

        <div className="max-h-0 overflow-hidden transition-max-height duration-300 peer-checked:max-h-screen">
          {restaurant.menu.map((section, sectionIndex) => (
            <div key={sectionIndex} className="mt-4">
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
    </div>
  );
};

export default RestaurantCard;
