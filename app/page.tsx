import menuData from "../public/menus.json";

export default function Home() {
  return (
    <div className="p-4">
      {menuData.map((restaurant) => (
        <div
          className="bg-white shadow-md rounded-lg p-6 mb-6"
          key={restaurant.name}
        >
          <h1 className="text-2xl font-bold mb-2">{restaurant.name}</h1>
          {restaurant.menu.dishes.length > 0 ? (
            <ul className="list-disc list-inside">
              {restaurant.menu.dishes.map((dish, index) => (
                <li className="text-gray-700 mb-2" key={index}>
                  {dish.name}{" "}
                  {dish.price && (
                    <span className="text-gray-500">- {dish.price}</span>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500">Ingen lunch serveras här idag</p>
          )}
        </div>
      ))}
    </div>
  );
}
