
import menuData from "../public/menus.json";
import logo from "../public/alvikslunchen.png";
import RestaurantCard from "./RestaurantCard";

export default function Home() {
  const sortedMenuData = menuData.restaurants.sort((a, b) =>
    a.name.localeCompare(b.name)
  );

  return (
    <div className="p-4">
      <img
        alt="logo"
        src={logo.src}
        className={"mx-auto sm:w-48 md:w-48 lg:w-48"}
      />
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {sortedMenuData.map((restaurant) => (
          <div key={restaurant.name} className="overflow-hidden">
            <RestaurantCard restaurant={restaurant} />
          </div>
        ))}
      </div>
    </div>
  );
}
