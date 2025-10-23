
import menuData from "../public/menus.json";
import logo from "../public/alvikslunchen.png";
import RestaurantCard from "./RestaurantCard";

export default function Home() {
  const sortedMenuData = menuData.restaurants.sort((a, b) =>
    a.name.localeCompare(b.name)
  );

  return (
    <div className="p-4">
      <section className="hero bg-zinc-800 text-center py-16">
        <h1 className="text-4xl font-bold text-gray-200">
          Upptäck dagens <span className="text-yellow-400">bästa</span> lunchalternativ i Alvik!
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
