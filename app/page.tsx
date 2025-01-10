import menuData from "../public/menus.json"

export default function Home() {
  return (
    <div className="p-4">
      {Object.entries(menuData).map(([restaurantName, menu]) => (
        <div className="bg-white shadow-md rounded-lg p-6 mb-6" key={restaurantName}>
          <h1 className="text-2xl font-bold mb-4">{restaurantName}</h1>
          {Object.entries(menu).map(([sectionName, items]) => (
            <div className="mb-4" key={sectionName}>
              {Array.isArray(items) ? (
                <>
                  <h2 className="text-xl font-semibold mb-2">{sectionName}</h2>
                  <ul className="list-disc list-inside">
                    {items.map((item, index) => (
                      <li className="text-gray-700 mb-2" key={index}>
                        {item}
                      </li>
                    ))}
                  </ul>
                </>
              ) : (
                <ul className="list-disc list-inside">
                  <li className="text-gray-700 mb-2">{items}</li>
                </ul>
              )}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
