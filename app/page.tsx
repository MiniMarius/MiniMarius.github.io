
import menuData from "../public/menus.json";
import logo from "../public/alvikslunchen.png";
import * as Accordion from "@radix-ui/react-accordion";
import { ChevronDownIcon } from "@radix-ui/react-icons";

export default function Home() {
  // Sort the menuData array alphabetically based on restaurant name
  const sortedMenuData = menuData.sort((a, b) => a.name.localeCompare(b.name));

  return (
    <div className="min-h-screen p-4">
      <img alt="logo" src={logo.src} className={"mx-auto sm:w-48 md:w-48 lg:w-48"} />
      <Accordion.Root type="multiple" className="space-y-4">
        {sortedMenuData.map((restaurant) => (
          <Accordion.Item value={restaurant.name} key={restaurant.name} className="bg-white shadow-md rounded-lg">
            <Accordion.Header>
              <Accordion.Trigger className="flex justify-between w-full p-6 font-bold text-2xl text-left items-center">
                {restaurant.name}
                <ChevronDownIcon className="ml-2" />
              </Accordion.Trigger>
            </Accordion.Header>
            <Accordion.Content className="p-6 border-t">
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
            </Accordion.Content>
          </Accordion.Item>
        ))}
      </Accordion.Root>
    </div>
  );
}
